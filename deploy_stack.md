# Two-Stack Architecture Deployment

This project has been split into two CloudFormation stacks for faster deployments and better separation of concerns:

### SAM Deploy
```bash
# 1. Deploy database stack first
sam deploy \
  --template-file database-stack.yaml \
  --stack-name membership-db-stack-dev \
  --parameter-overrides Stage=dev \
  --capabilities CAPABILITY_IAM

# 2. Deploy API stack (references database stack)
sam build --template api-stack.yaml
sam deploy \
  --template-file api-stack.yaml \
  --stack-name membership-api-stack-dev \
  --parameter-overrides Stage=dev DatabaseStackName=membership-db-stack-dev \
  --capabilities CAPABILITY_IAM CAPABILITY_AUTO_EXPAND
```

## Stack Dependencies

The API stack imports these values from the database stack:
- `VPC-ID` → VPC for Lambda placement
- `PrivateSubnet1-ID`, `PrivateSubnet2-ID` → Subnets for Lambda
- `LambdaSecurityGroup-ID` → Security group for Lambda
- `Database-Endpoint` → RDS endpoint
- `Database-Port` → RDS port
- `Database-Name` → Database name
- `Database-Secret-ARN` → Secrets Manager ARN

## Why Two-Stack Architecture

### 1. **Faster API Deployments**
- Database stack deployed once: ~15 minutes
- Subsequent API deployments: ~3 minutes
- Perfect for CI/CD pipelines

### 2. **Early Validation**
- Database configuration errors caught immediately
- API stack won't deploy if database stack fails
- Fail-fast approach saves time

### 3. **Environment Isolation**
- Different database stacks per environment
- Shared VPC infrastructure
- Independent API deployments

### 4. **Production-Grade Pattern**
- Standard practice for enterprise deployments
- Clear separation of infrastructure vs application
- Easier rollbacks and maintenance


## Stack Names

The deployment script uses this naming convention:
- Database Stack: `membership-db-stack-{stage}`
- API Stack: `membership-api-stack-{stage}`

## Environment Variables

The Lambda function receives these environment variables from the database stack:
- `DB_HOST` - RDS endpoint
- `DB_PORT` - RDS port (5432)
- `DB_NAME` - Database name
- `DB_SECRET_ARN` - Secrets Manager ARN for credentials
- `COGNITO_USER_POOL_ID` - From API stack
- `COGNITO_CLIENT_ID` - From API stack