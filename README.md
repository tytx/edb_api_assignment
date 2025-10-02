# Membership REST API - AWS Serverless Architecture

A production-ready simple serverless REST API for managing membership sign-ups, built with FastAPI, AWS Lambda (docker), RDS PostgreSQL, and AWS Cognito authentication (OAuth 2.0).

## Table of Contents
- [Architecture Overview](#architecture-overview)
- [OpenAPI Specification](#openapi-specification)
- [AWS Configuration](#aws-configuration)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Deployment](#deployment)
- [Local Development](#local-development)
- [Testing with Postman](#testing-with-postman)

---

## Architecture Overview

This project uses a **two-stack CloudFormation architecture** for efficient AWS SAM deployments:

### Stack 1: Database Stack ([database-stack.yaml](database-stack.yaml))
**Infrastructure Layer** - Long-lived resources that rarely change
- VPC with public/private subnets across 2 availability zones
- NAT Gateway for Lambda internet access
- RDS PostgreSQL 16.10 (db.t3.micro)
- AWS Secrets Manager for database credentials
- Security groups for Lambda and RDS

**Deployment time:** ~10-15 minutes (initial setup)

### Stack 2: API Stack ([api-stack.yaml](api-stack.yaml))
**Application Layer** - Frequently updated resources
- Lambda function (containerized FastAPI)
- API Gateway with Cognito authentication
- AWS Cognito User Pool for user management
- Environment variables injected from database stack

**Deployment time:** ~2-3 minutes (subsequent updates)

### Why Two Stacks?
1. **Faster iterations** - API changes deploy in minutes, not waiting for RDS
2. **Early validation** - Database issues caught before API deployment
3. **Cost efficiency** - Database infrastructure deployed once
4. **Production pattern** - Industry-standard separation of concerns

---

## OpenAPI Specification

The API follows the OpenAPI 3.0 specification defined in [member.spec.yaml](member.spec.yaml).

### Base URL
```
https://{api-id}.execute-api.{region}.amazonaws.com/{stage}/
```

### Endpoints

#### 1. Health Check
```http
GET /health
```
**Description:** Check API health status
**Authentication:** None required
**Response:**
```json
{
  "status": "healthy",
  "service": "membership-api",
  "environment": "lambda"
}
```

#### 2. Create Member
```http
POST /members
Content-Type: application/json
Authorization: Bearer {cognito_token}
```
**Request Body:**
```json
{
  "firstName": "John",
  "lastName": "Doe",
  "email": "john.doe@example.com", // unique
  "phone": 1234567890,
  "age": 30,
  "isEmployee": false
}
```

**Response (201 Created):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "firstName": "John",
  "lastName": "Doe",
  "email": "john.doe@example.com",
  "phone": 1234567890,
  "age": 30,
  "isEmployee": false,
  "createdAt": "2025-01-15T10:30:00Z"
}
```

#### 3. Get specific members by name
```http
GET /members?firstName=John&lastName=Doe
Authorization: Bearer {cognito_token}
```
**Query Parameters:**
- `firstName` (optional): Filter by first name
- `lastName` (optional): Filter by last name

**Response (200 OK):**
```json
{
  "message": "Members retrieved successfully",
  "members": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "firstName": "John",
      "lastName": "Doe",
      "email": "john.doe@example.com",
      "createdAt": "2025-01-15T10:30:00Z"
    }
  ]
}
```

#### 4. Get specific Member by ID
```http
GET /members/{id}
Authorization: Bearer {cognito_token}
```
**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "firstName": "John",
  "lastName": "Doe",
  "email": "john.doe@example.com",
  "phone": 1234567890,
  "age": 30,
  "isEmployee": false,
  "createdAt": "2025-01-15T10:30:00Z"
}
```

### Data Validation
- **Email:** Must be valid email format
- **Phone:** Integer type (e.g., 1234567890)
- **Age:** Integer type
- **Required fields:** firstName, lastName, email

---

## AWS Configuration

### Required AWS Services

#### 1. VPC & Networking
- **VPC CIDR:** 10.0.0.0/16
- **Public Subnets:** 10.0.10.0/24, 10.0.11.0/24 (NAT Gateway placement)
- **Private Subnets:** 10.0.1.0/24, 10.0.2.0/24 (Lambda & RDS placement)
- **Internet Gateway:** Public subnet routing
- **NAT Gateway:** Private subnet internet access (for Lambda)

#### 2. RDS PostgreSQL
| Parameter | Value | Notes |
|-----------|-------|-------|
| Engine | PostgreSQL | Version 16.10 |
| Instance Class | db.t3.micro | Default (configurable) |
| Storage | 20GB GP2 | Auto-scaling enabled |
| Multi-AZ | false | Can be enabled for production |
| Encryption | Enabled | AWS KMS encryption |
| Backup Retention | 7 days | Daily automated backups |
| Port | 5432 | Standard PostgreSQL port |

**Database Credentials:**
- Stored in AWS Secrets Manager
- Auto-generated password (16 characters)
- Accessed by Lambda via IAM policy

#### 3. AWS Lambda
| Parameter | Value |
|-----------|-------|
| Runtime | Python 3.10 (Container) |
| Memory | 512 MB |
| Timeout | 30 seconds |
| Architecture | x86_64 |
| Deployment | Docker image via ECR |

**Environment Variables:**
- `DB_HOST` - RDS endpoint address
- `DB_PORT` - RDS port (5432)
- `DB_NAME` - Database name (membership_db)
- `DB_SECRET_ARN` - Secrets Manager ARN
- `COGNITO_USER_POOL_ID` - User Pool ID
- `COGNITO_CLIENT_ID` - User Pool Client ID
- `NOTIFICATION_EMAIL` - Email for member notifications
- `AWS_REGION_NAME` - AWS region

**IAM Permissions:**
- `secretsmanager:GetSecretValue` - Access database credentials
- `ses:SendEmail` - Send notification emails (on POST Requests i.e. API caller's email)
- `ec2:CreateNetworkInterface` - VPC access (Lambda managed)

#### 4. AWS Cognito
**User Pool Configuration:**
- Auto-verified attributes: email
- Password policy:
  - Minimum length: 8 characters
  - Require uppercase, lowercase, numbers
  - Symbols optional

**App Client Settings:**
- Auth flows: USER_PASSWORD_AUTH, ADMIN_USER_PASSWORD_AUTH, REFRESH_TOKEN_AUTH
- OAuth flows: code, implicit
- OAuth scopes: email, openid, profile
- Callback URL: `https://oauth.pstmn.io/v1/callback` (Postman testing)

**Domain:**
- Format: `{stack-name}-{aws-account-id}.auth.{region}.amazoncognito.com`

#### 5. API Gateway
| Setting | Value |
|---------|-------|
| Stage | dev/ |
| Authorizer | Cognito User Pool |
| CORS | Enabled (all origins) |
| Throttling | 50 requests/sec, 100 burst |
| Security Headers | X-Frame-Options, X-XSS-Protection |

#### 6. AWS SES (Simple Email Service)
**Purpose:** Send notifications when new members sign up
**Configuration:**
1. Verify sender email in SES console
2. Request production access (if needed)
3. Update `NotificationEmail` parameter in [api-stack.yaml](api-stack.yaml)

---

## Project Structure

```
rest_api_edb/
├── app/                          # FastAPI application code
│   ├── database/                 # Database connection & models
│   │   ├── database.py           # SQLAlchemy engine setup
│   │   └── db_model.py           # Member table schema
│   ├── models/                   # Pydantic models
│   │   └── member_model.py       # Request/response schemas
│   ├── routes/                   # API route handlers
│   │   └── members.py            # /members endpoints
│   ├── services/                 # Business logic
│   │   ├── member_service.py     # CRUD operations
│   │   └── notification_service.py  # Email notifications
│   ├── utils/                    # Utility functions
│   ├── Dockerfile                # Lambda container definition
│   ├── lambda_handler.py         # Mangum adapter for Lambda
│   ├── main.py                   # FastAPI app initialization
│   ├── requirements.txt          # Python dependencies
│   └── seed.py                   # Sample data seeder
│
├── api-stack.yaml                # CloudFormation: Lambda, API Gateway, Cognito
├── database-stack.yaml           # CloudFormation: VPC, RDS, Secrets
├── member.spec.yaml              # OpenAPI 3.0 specification
├── samconfig.toml                # SAM deployment configuration
├── docker-compose.yaml           # Local PostgreSQL for development
├── .env.example                  # Environment variable template
├── pass.sh / pass.ps1            # Helper scripts for password setup
```

### Key Application Files

#### [app/main.py](app/main.py)
FastAPI application entry point with health check and router registration.

#### [app/lambda_handler.py](app/lambda_handler.py)
Mangum adapter to run FastAPI on AWS Lambda.

#### [app/routes/members.py](app/routes/members.py)
Route handlers for member CRUD operations.

#### [app/services/member_service.py](app/services/member_service.py)
Business logic for member management and database operations.

#### [app/models/member_model.py](app/models/member_model.py)
Pydantic schemas for request validation and response serialization.

---

## Prerequisites

### Required Tools
- **AWS CLI** - [Install guide](https://aws.amazon.com/cli/)
- **AWS SAM CLI** - [Install guide](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html)
- **Docker** - [Install guide](https://docs.docker.com/get-docker/)
- **Python 3.10+** - [Download](https://www.python.org/downloads/)

### AWS Account Setup
1. Configure AWS credentials:
   ```bash
   aws configure
   ```
2. Ensure you have permissions to create:
   - VPC, Subnets, NAT Gateway
   - RDS instances
   - Lambda functions
   - API Gateway APIs
   - Cognito User Pools
   - Secrets Manager secrets

---

## Deployment

### 1. Deploy Database Stack (First Time Only)
```bash
sam deploy \
  --template-file database-stack.yaml \
  --stack-name membership-db-stack-dev \
  --parameter-overrides Stage=dev \
  --capabilities CAPABILITY_IAM
```

**Outputs to note:**
- VPC ID
- RDS Endpoint
- Database Secret ARN

**⏱️ Deployment time:** ~10-15 minutes

### 2. Deploy API Stack
```bash
# Build the Docker image
sam build --template api-stack.yaml

# Deploy to AWS
sam deploy `
  --template-file .aws-sam/build/template.yaml `
  --stack-name membership-api-stack-dev `
  --region us-east-1 `
  --parameter-overrides Stage=dev DatabaseStackName=membership-db-stack-dev NotificationEmail=telsonting@gmail.com `
  --capabilities CAPABILITY_IAM CAPABILITY_AUTO_EXPAND `
  --no-fail-on-empty-changeset `
  --resolve-image-repos `
  --resolve-s3
```

**Outputs to note:**
- API Gateway URL
- Cognito User Pool ID
- Cognito Client ID

**⏱️ Deployment time:** ~2-3 minutes

### 3. Post-Deployment Steps

#### Create Cognito User Example
```bash
USER_POOL_ID=$(aws cloudformation describe-stacks \
  --stack-name membership-api-stack-dev \
  --query "Stacks[0].Outputs[?OutputKey=='UserPoolId'].OutputValue" \
  --output text)

aws cognito-idp admin-create-user \
  --user-pool-id $USER_POOL_ID \
  --username testuser \
  --temporary-password TempPassword123! \
  --user-attributes Name=email,Value=test@example.com \
  --message-action SUPPRESS

aws cognito-idp admin-set-user-password \
  --user-pool-id $USER_POOL_ID \
  --username testuser \
  --password MyPassword123! \
  --permanent
```

---

## Testing with Postman

### 3. Configure OAuth 2.0 Authentication in Postman

1. **Get Cognito Domain from CloudFormation:**
   ```bash
   aws cloudformation describe-stacks \
     --stack-name membership-api-stack-dev \
     --query "Stacks[0].Outputs[?OutputKey=='CognitoDomain'].OutputValue" \
     --output text
   ```

2. **In Postman, go to Authorization tab:**
   - Type: `OAuth 2.0`
   - Add auth data to: `Request Headers`

3. **Configure New Token:**
   - **Token Name:** `Cognito Access Token`
   - **Grant Type:** `Authorization Code` or `Implicit`
   - **Callback URL:** `https://oauth.pstmn.io/v1/callback`
   - **Auth URL:** `https://{{COGNITO_DOMAIN}}/oauth2/authorize`
     - Example: `https://membership-api-stack-dev-123456789.auth.us-east-1.amazoncognito.com/oauth2/authorize`
   - **Access Token URL:** `https://{{COGNITO_DOMAIN}}/oauth2/token`
     - Example: `https://membership-api-stack-dev-123456789.auth.us-east-1.amazoncognito.com/oauth2/token`
   - **Client ID:** `{{CLIENT_ID}}` (see: https://share.doppler.com/s/wzhpd9llwds9s1cpgynqekkn6ke7syoqfbnjtqrs#rj5CHePJ2Aqz3Iy8waS6wbljz5HTCeBCngODd9JR4QD68n2ugmu1FkOmi2EfITQI)
   - **Client Secret:** Leave empty (public client)
   - **Scope:** `email openid profile`
   - **State:** (auto-generated)
   - **Client Authentication:** `Send as Basic Auth header`

4. **Click "Get New Access Token"**
   - Postman will open a browser window
   - Sign in with your Cognito user credentials:
   https://share.doppler.com/s/da6y5ukztgczhwjmi7puq2fjry88cgxvvkawehbn#MFShHEfdEChrt5vF2AHizjunIIb7x7QzePDphGh19FQVfnpgFD2ZN6gQiAIKYWw7
   - Token will be automatically added to requests

5. **Use Token:**
   - Click "Use Token"
   - Token will be added as `Authorization: Bearer {token}` header

### 4. Test Endpoints

#### API URL: `https://39jc3q03w9.execute-api.us-east-1.amazonaws.com/dev/members?firstName=John`

#### Health Check (No Auth Required)
```http
GET {{API_URL}}/health
```

#### Create Member (Auth Required)
```http
POST {{API_URL}}/members
Content-Type: application/json

{
  "firstName": "John",
  "lastName": "Doe",
  "email": "john@example.com",
  "phone": 1234567890,
  "age": 30,
  "isEmployee": false
}
```

#### Get Members by Name (Auth Required)
```http
GET {{API_URL}}/members?firstName=John&lastName=Doe
```

#### Get Member by ID (Auth Required)
```http
GET {{API_URL}}/members/{id}
```



