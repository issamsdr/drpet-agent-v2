# 🚀 DRPET Agent v2 - AWS Deployment Guide

## Quick Deployment (5 minutes)

### Prerequisites
1. **AWS CLI configured** with appropriate permissions
2. **Docker installed** and running
3. **Python 3.8+** installed
4. **Bash shell** (Linux/macOS/WSL)

### One-Command Deployment
```bash
# Make the deployment script executable
chmod +x deployment/deploy-drpet-agent.sh

# Deploy to your AWS account
./deployment/deploy-drpet-agent.sh
```

The script will:
- ✅ Check prerequisites
- ✅ Create S3 deployment bucket
- ✅ Package and upload code
- ✅ Deploy infrastructure (VPC, ECS, ALB, etc.)
- ✅ Deploy application containers
- ✅ Run validation tests
- ✅ Display access URLs

## What Gets Deployed

### Infrastructure Components
- **VPC** with public/private subnets across 2 AZs
- **ECS Fargate cluster** for container hosting
- **Application Load Balancer** for traffic distribution
- **API Gateway** for REST API access
- **CloudWatch** for logging and monitoring
- **IAM roles** with least-privilege permissions
- **Security groups** with minimal required access

### Application Components
- **DRPET Agent containers** running on ECS Fargate
- **Auto-scaling** based on CPU/memory utilization
- **Health checks** and monitoring
- **Performance optimization** with caching and parallel processing
- **Security hardening** with circuit breakers and rate limiting

## Access Your Deployment

After deployment completes, you'll see output like:
```
==========================================
DRPET Agent v2 Deployment Complete!
==========================================
Environment: production
Region: us-east-1
API URL: https://abc123.execute-api.us-east-1.amazonaws.com/production
Load Balancer URL: http://drpet-agent-alb-123456789.us-east-1.elb.amazonaws.com
==========================================
```

### API Endpoints
- **Health Check**: `GET /health`
- **System Status**: `GET /status`
- **Metrics**: `GET /metrics`
- **Whitepaper Analysis**: `POST /analyze/whitepaper`
- **Service Analysis**: `POST /analyze/services`
- **Comprehensive Analysis**: `POST /analyze/comprehensive`
- **API Documentation**: `GET /docs`

## Validation

### Run Production Readiness Check
```bash
python3 validate_drpet_production_readiness.py --save-report
```

### Run Integration Tests
```bash
python3 test_production_integration.py
```

### Test API Endpoints
```bash
# Health check
curl https://your-api-url/health

# System status
curl https://your-api-url/status

# API documentation
open https://your-api-url/docs
```

## Configuration

### Environment Variables
The deployment supports these environment variables:
- `ENVIRONMENT`: deployment environment (production, staging, development)
- `AWS_DEFAULT_REGION`: AWS region for deployment
- `LOG_LEVEL`: logging level (INFO, DEBUG, WARNING, ERROR)

### Custom Configuration
```bash
# Deploy to staging environment
./deployment/deploy-drpet-agent.sh -e staging -r us-west-2

# Deploy with custom settings
ENVIRONMENT=staging AWS_DEFAULT_REGION=eu-west-1 ./deployment/deploy-drpet-agent.sh
```

## Required AWS Permissions

Your AWS credentials need these permissions:
- **CloudFormation**: Full access for stack management
- **ECS**: Full access for container orchestration
- **EC2**: Full access for VPC and networking
- **IAM**: Full access for role creation
- **S3**: Full access for deployment artifacts
- **Lambda**: Full access for build functions
- **API Gateway**: Full access for API management
- **CloudWatch**: Full access for logging and monitoring
- **ECR**: Full access for container registry

## Cost Estimate

Monthly costs (approximate):
- **ECS Fargate**: $50-200 (depending on usage)
- **Application Load Balancer**: $20
- **NAT Gateways**: $45 (2 AZs)
- **CloudWatch Logs**: $5-20
- **API Gateway**: $3.50 per million requests
- **Total**: ~$125-290/month

## Troubleshooting

### Common Issues

#### 1. AWS Credentials Not Configured
```bash
aws configure
# Enter your AWS Access Key ID, Secret Access Key, and region
```

#### 2. Docker Not Running
```bash
# Start Docker
sudo systemctl start docker  # Linux
# or
open -a Docker  # macOS
```

#### 3. Insufficient Permissions
Ensure your AWS user/role has the required permissions listed above.

#### 4. Deployment Fails
```bash
# Check CloudFormation events
aws cloudformation describe-stack-events --stack-name drpet-agent-v2-infrastructure

# Check logs
aws logs describe-log-groups --log-group-name-prefix "/aws/drpet-agent"
```

### Get Help
- Check the detailed deployment guide: `deployment/README.md`
- Review troubleshooting docs: `docs/drpet-troubleshooting-maintenance.md`
- Run validation script for diagnostics: `validate_drpet_production_readiness.py`

## Next Steps

After successful deployment:

1. **Configure Authentication** (if needed)
2. **Set up Monitoring Alerts**
3. **Run Integration Tests**
4. **Train Your Team**
5. **Start Using DRPET for Customer Engagements**

## Cleanup

To remove the deployment:
```bash
# Delete application stack
aws cloudformation delete-stack --stack-name drpet-agent-v2-application

# Delete infrastructure stack (after application stack is deleted)
aws cloudformation delete-stack --stack-name drpet-agent-v2-infrastructure

# Delete S3 deployment bucket (optional)
aws s3 rb s3://drpet-agent-deployment-$(aws sts get-caller-identity --query Account --output text)-us-east-1 --force
```

---

## Support

For additional support:
- 📖 **Detailed Documentation**: See `deployment/README.md`
- 🔧 **Troubleshooting**: See `docs/drpet-troubleshooting-maintenance.md`
- 🧪 **Testing**: Run `validate_drpet_production_readiness.py`
- 📊 **Monitoring**: Check CloudWatch dashboards and logs

**Ready to deploy? Run `./deployment/deploy-drpet-agent.sh` to get started!** 🚀