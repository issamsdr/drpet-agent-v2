#!/bin/bash

# DRPET Agent v2 Deployment Script
# This script deploys the DRPET Agent to your AWS account using the AWS Operations Agent foundation

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
STACK_NAME="drpet-agent-v2"
REGION="${AWS_DEFAULT_REGION:-us-east-1}"
ENVIRONMENT="${ENVIRONMENT:-production}"
DEPLOYMENT_BUCKET=""

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking deployment prerequisites..."
    
    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI is not installed. Please install it first."
        exit 1
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        print_error "AWS credentials not configured. Please run 'aws configure' first."
        exit 1
    fi
    
    # Check Docker (for container builds)
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3.8+ first."
        exit 1
    fi
    
    # Get AWS Account ID
    AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    print_success "AWS Account ID: $AWS_ACCOUNT_ID"
    
    # Set deployment bucket name
    DEPLOYMENT_BUCKET="drpet-agent-deployment-${AWS_ACCOUNT_ID}-${REGION}"
    
    print_success "Prerequisites check completed"
}

# Function to create S3 deployment bucket
create_deployment_bucket() {
    print_status "Creating deployment S3 bucket..."
    
    if aws s3 ls "s3://$DEPLOYMENT_BUCKET" 2>&1 | grep -q 'NoSuchBucket'; then
        if [ "$REGION" = "us-east-1" ]; then
            aws s3 mb "s3://$DEPLOYMENT_BUCKET"
        else
            aws s3 mb "s3://$DEPLOYMENT_BUCKET" --region "$REGION"
        fi
        
        # Enable versioning
        aws s3api put-bucket-versioning \
            --bucket "$DEPLOYMENT_BUCKET" \
            --versioning-configuration Status=Enabled
        
        print_success "Created deployment bucket: $DEPLOYMENT_BUCKET"
    else
        print_status "Deployment bucket already exists: $DEPLOYMENT_BUCKET"
    fi
}

# Function to package and upload code
package_and_upload() {
    print_status "Packaging DRPET Agent code..."
    
    # Create temporary directory
    TEMP_DIR=$(mktemp -d)
    PACKAGE_DIR="$TEMP_DIR/drpet-agent"
    
    # Copy source code
    mkdir -p "$PACKAGE_DIR"
    cp -r src/ "$PACKAGE_DIR/"
    cp -r deployment/ "$PACKAGE_DIR/"
    cp requirements.txt "$PACKAGE_DIR/" 2>/dev/null || echo "# DRPET Agent dependencies" > "$PACKAGE_DIR/requirements.txt"
    
    # Add deployment-specific requirements
    cat >> "$PACKAGE_DIR/requirements.txt" << EOF
boto3>=1.26.0
botocore>=1.29.0
fastapi>=0.68.0
uvicorn>=0.15.0
psutil>=5.8.0
requests>=2.25.0
pydantic>=1.8.0
python-multipart>=0.0.5
aiofiles>=0.7.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
python-dotenv>=0.19.0
EOF
    
    # Create deployment package
    cd "$TEMP_DIR"
    zip -r "drpet-agent-${ENVIRONMENT}.zip" drpet-agent/
    
    # Upload to S3
    aws s3 cp "drpet-agent-${ENVIRONMENT}.zip" "s3://$DEPLOYMENT_BUCKET/packages/"
    
    print_success "Code package uploaded to S3"
    
    # Cleanup
    rm -rf "$TEMP_DIR"
}

# Function to deploy infrastructure
deploy_infrastructure() {
    print_status "Deploying DRPET Agent infrastructure..."
    
    # Deploy CloudFormation stack
    aws cloudformation deploy \
        --template-file deployment/cloudformation/drpet-infrastructure.yaml \
        --stack-name "$STACK_NAME-infrastructure" \
        --parameter-overrides \
            Environment="$ENVIRONMENT" \
            DeploymentBucket="$DEPLOYMENT_BUCKET" \
        --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
        --region "$REGION"
    
    print_success "Infrastructure deployment completed"
}

# Function to deploy application
deploy_application() {
    print_status "Deploying DRPET Agent application..."
    
    # Get infrastructure outputs
    VPC_ID=$(aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME-infrastructure" \
        --query 'Stacks[0].Outputs[?OutputKey==`VpcId`].OutputValue' \
        --output text \
        --region "$REGION")
    
    SUBNET_IDS=$(aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME-infrastructure" \
        --query 'Stacks[0].Outputs[?OutputKey==`PrivateSubnetIds`].OutputValue' \
        --output text \
        --region "$REGION")
    
    SECURITY_GROUP_ID=$(aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME-infrastructure" \
        --query 'Stacks[0].Outputs[?OutputKey==`SecurityGroupId`].OutputValue' \
        --output text \
        --region "$REGION")
    
    # Deploy application stack
    aws cloudformation deploy \
        --template-file deployment/cloudformation/drpet-application.yaml \
        --stack-name "$STACK_NAME-application" \
        --parameter-overrides \
            Environment="$ENVIRONMENT" \
            VpcId="$VPC_ID" \
            SubnetIds="$SUBNET_IDS" \
            SecurityGroupId="$SECURITY_GROUP_ID" \
            DeploymentBucket="$DEPLOYMENT_BUCKET" \
            CodePackageKey="packages/drpet-agent-${ENVIRONMENT}.zip" \
        --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
        --region "$REGION"
    
    print_success "Application deployment completed"
}

# Function to run post-deployment validation
run_validation() {
    print_status "Running post-deployment validation..."
    
    # Wait for services to be ready
    sleep 30
    
    # Run validation script
    if [ -f "validate_drpet_production_readiness.py" ]; then
        python3 validate_drpet_production_readiness.py --save-report
        
        if [ $? -eq 0 ]; then
            print_success "Post-deployment validation passed"
        else
            print_warning "Post-deployment validation failed - check the report for details"
        fi
    else
        print_warning "Validation script not found - skipping validation"
    fi
}

# Function to display deployment information
display_deployment_info() {
    print_status "Retrieving deployment information..."
    
    # Get API Gateway URL
    API_URL=$(aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME-application" \
        --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
        --output text \
        --region "$REGION" 2>/dev/null || echo "Not available")
    
    # Get Load Balancer URL
    LB_URL=$(aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME-application" \
        --query 'Stacks[0].Outputs[?OutputKey==`LoadBalancerUrl`].OutputValue' \
        --output text \
        --region "$REGION" 2>/dev/null || echo "Not available")
    
    echo ""
    echo "=========================================="
    echo "DRPET Agent v2 Deployment Complete!"
    echo "=========================================="
    echo "Environment: $ENVIRONMENT"
    echo "Region: $REGION"
    echo "Stack Name: $STACK_NAME"
    echo "API URL: $API_URL"
    echo "Load Balancer URL: $LB_URL"
    echo "Deployment Bucket: $DEPLOYMENT_BUCKET"
    echo ""
    echo "Next Steps:"
    echo "1. Configure OAuth2 authentication"
    echo "2. Set up monitoring and alerting"
    echo "3. Run integration tests"
    echo "4. Update DNS records if needed"
    echo "=========================================="
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -e, --environment ENV    Deployment environment (default: production)"
    echo "  -r, --region REGION      AWS region (default: us-east-1)"
    echo "  -h, --help              Show this help message"
    echo ""
    echo "Environment variables:"
    echo "  AWS_DEFAULT_REGION      AWS region to deploy to"
    echo "  ENVIRONMENT            Deployment environment"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Deploy to production in us-east-1"
    echo "  $0 -e staging -r us-west-2          # Deploy to staging in us-west-2"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -r|--region)
            REGION="$2"
            shift 2
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Main deployment flow
main() {
    echo "=========================================="
    echo "DRPET Agent v2 Deployment Script"
    echo "=========================================="
    echo "Environment: $ENVIRONMENT"
    echo "Region: $REGION"
    echo ""
    
    # Confirm deployment
    read -p "Do you want to proceed with the deployment? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_status "Deployment cancelled"
        exit 0
    fi
    
    # Run deployment steps
    check_prerequisites
    create_deployment_bucket
    package_and_upload
    deploy_infrastructure
    deploy_application
    run_validation
    display_deployment_info
    
    print_success "DRPET Agent v2 deployment completed successfully!"
}

# Run main function
main "$@"