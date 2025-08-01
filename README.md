# DRPET Agent v2

**AWS Disaster Recovery Planning and Execution Tool - Agent v2**

An advanced agentic automated application designed for AWS Technical Account Managers to streamline AWS Enterprise Support's DrPET (Disaster Recovery Planning and Execution Tool) engagement process.

## 🚀 Quick Start

### Deploy to AWS (5 minutes)
```bash
# Make deployment script executable
chmod +x deployment/deploy-drpet-agent.sh

# Deploy to your AWS account
./deployment/deploy-drpet-agent.sh
```

### Validate Deployment
```bash
# Run production readiness validation
python3 validate_drpet_production_readiness.py --save-report
```

## 🏗️ Architecture

Built on the proven AWS Operations Agent foundation with:
- **Strands Framework Integration** for agentic capabilities
- **MCP Tool Integration** with 20+ AWS services
- **Performance Optimization** with caching and parallel processing
- **Production Hardening** with circuit breakers and rate limiting
- **Comprehensive Monitoring** with health checks and alerting

## 🎯 Key Features

### Digital SME Automation
- **Replaces manual SME coordination** with autonomous AI agent capabilities
- **Automates Discovery, Deep Dive, and Live-Fire Testing phases**
- **Eliminates bottlenecks** in traditional DrPET process flow
- **24/7 availability** without human scheduling constraints

### Comprehensive Analysis
- **6 AWS Resilience Whitepapers** compliance analysis
- **20+ AWS Services** resilience assessment
- **RHR Generation** with Trusted Advisor integration
- **Service-specific checks** for EC2, RDS, S3, DynamoDB, Lambda, etc.

### Enterprise-Grade Performance
- **Multi-level caching** reduces analysis time by 80%
- **Parallel processing** improves speed by 5-10x
- **Intelligent batching** for large-scale assessments
- **Memory optimization** prevents resource leaks

### Production Hardening
- **Circuit breakers** prevent cascade failures
- **Rate limiting** protects against abuse
- **Security validation** prevents injection attacks
- **Comprehensive error handling** with retry logic

## 📁 Project Structure

```
drpet-agent-v2/
├── src/drpet_agent/           # Main application code
│   ├── analysis/              # Analysis engines
│   ├── core/                  # Core utilities
│   ├── mcp_tools/            # MCP tool handlers
│   ├── monitoring/           # Health checks & alerting
│   └── main.py               # FastAPI application
├── deployment/               # AWS deployment automation
│   ├── cloudformation/       # CloudFormation templates
│   └── deploy-drpet-agent.sh # One-click deployment
├── docs/                     # Documentation
├── training/                 # Training materials
├── .kiro/spec/              # Project specifications
└── tests/                   # Test suites
```

## 🔧 API Endpoints

- **Health Check**: `GET /health`
- **System Status**: `GET /status`
- **Metrics**: `GET /metrics`
- **Whitepaper Analysis**: `POST /analyze/whitepaper`
- **Service Analysis**: `POST /analyze/services`
- **Comprehensive Analysis**: `POST /analyze/comprehensive`
- **API Documentation**: `GET /docs`

## 📊 What Gets Deployed

### Infrastructure
- VPC with public/private subnets across 2 AZs
- ECS Fargate cluster with auto-scaling
- Application Load Balancer
- API Gateway with VPC Link
- CloudWatch monitoring and logging
- IAM roles with least-privilege permissions

### Cost Estimate
~$125-290/month depending on usage

## 🛠️ Prerequisites

- AWS CLI configured with appropriate permissions
- Docker installed and running
- Python 3.8+ installed
- Bash shell (Linux/macOS/WSL)

## 📚 Documentation

- **[Deployment Guide](DEPLOYMENT_GUIDE.md)** - Quick start deployment
- **[Detailed Deployment](deployment/README.md)** - Comprehensive deployment guide
- **[API Reference](docs/drpet-api-reference.md)** - Complete API documentation
- **[Troubleshooting](docs/drpet-troubleshooting-maintenance.md)** - Common issues and solutions
- **[Training Materials](training/)** - User training and best practices

## 🧪 Testing

```bash
# Run production readiness validation
python3 validate_drpet_production_readiness.py

# Run integration tests
python3 test_production_integration.py
```

## 🔒 Security

- OAuth2/JWT authentication
- Input validation and sanitization
- Rate limiting and circuit breakers
- Encryption in transit and at rest
- Least privilege IAM roles

## 📈 Performance

- **Multi-level caching** for analysis results
- **Parallel processing** for multiple services
- **Intelligent batching** for large workloads
- **Memory optimization** with automatic cleanup
- **Circuit breakers** for external dependencies

## 🚨 Monitoring

- Comprehensive health checks
- Real-time alerting system
- Performance metrics collection
- CloudWatch dashboards
- Automated backup systems

## 🤝 Contributing

This is an internal AWS Enterprise Support tool. For contributions:
1. Follow the existing code structure
2. Add comprehensive tests
3. Update documentation
4. Ensure security compliance

## 📄 License

Internal AWS Enterprise Support tool - All rights reserved.

## 🆘 Support

- **Documentation**: Check the `docs/` directory
- **Troubleshooting**: Run validation scripts
- **Issues**: Use GitHub issues for bug reports
- **Training**: See `training/` directory

---

**Ready to deploy?** Run `./deployment/deploy-drpet-agent.sh` to get started! 🚀