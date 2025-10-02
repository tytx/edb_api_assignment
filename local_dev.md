# Local Development Guide

This guide covers setting up and running the Membership API locally for development.

## Prerequisites

- Python 3.10+
- Docker & Docker Compose
- PostgreSQL client (optional, for database inspection)

## Quick Start

### 1. Clone and Navigate to Project

```bash
cd rest_api_edb
```

### 2. Set Up Environment Variables

Copy the example environment file and update it:

```bash
cp .env.example .env
```

Edit [.env](.env) with your configuration:

```env
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=members
DB_USER=user
DB_PASSWORD=password
```
# API Authentication (Local Development Only)
see: https://share.doppler.com/s/vxyafttalcjfm5vbwzem0bwwmj4igzznyc8lzfid#bt7B7O1hiQ0rGeCHo2Yp6DNAfgpoYusUHKWH4JaE5dlourWgpu5zPtBNXJIB9ATA 


**Note:** The `API_KEY` is used for local development authentication. In production, AWS Cognito handles authentication.

### 3. Start PostgreSQL Database

Start the PostgreSQL container using Docker Compose:

```bash
docker-compose up -d
```

Verify the database is running:

```bash
docker ps
```

### 4. Set Up Python Environment

Create and activate a virtual environment:

**Linux/Mac:**
```bash
python -m venv venv
source venv/bin/activate
```

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

### 5. Install Dependencies

```bash
pip install -r app/requirements.txt
```

### 6. Run the API

Start the development server:

```bash
cd app
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

## API Documentation

Once the server is running, access the interactive API documentation:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)

## Key Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/health` | Health check | No |
| GET | `/members` | Get members by name | Yes |
| POST | `/members` | Create new member | Yes |
| GET | `/members/{id}` | Get member by ID | Yes |

### Authentication

All endpoints except `/health` require an API key in the request header:

https://share.doppler.com/s/vxyafttalcjfm5vbwzem0bwwmj4igzznyc8lzfid#bt7B7O1hiQ0rGeCHo2Yp6DNAfgpoYusUHKWH4JaE5dlourWgpu5zPtBNXJIB9ATA

**Note:** This is for local development only. In production, AWS Cognito OAuth 2.0 is used.

## Database Management

### Access PostgreSQL Container

```bash
docker exec -it members-postgres psql -U user -d members
```

### View Tables

```sql
\dt
```

### View Sample Data

The application automatically seeds a sample member on first run:

```sql
SELECT * FROM members;
```

### Reset Database

Stop and remove the container with volumes:

```bash
docker-compose down -v
docker-compose up -d
```

## Project Structure

```
rest_api_edb/
├── app/
│   ├── database/
│   │   ├── database.py       # Database connection
│   │   └── db_model.py       # SQLAlchemy models
│   ├── models/
│   │   └── member_model.py   # Pydantic models
│   ├── routes/
│   │   └── members.py        # API routes
│   ├── services/
│   │   ├── member_service.py        # Business logic
│   │   └── notification_service.py  # Email notifications
│   ├── utils/
│   │   └── sanitization.py   # Input sanitization
│   ├── main.py               # FastAPI application
│   ├── lambda_handler.py     # AWS Lambda handler
│   ├── seed.py               # Database seeding
│   ├── requirements.txt      # Python dependencies
│   └── Dockerfile           # Container image
├── docker-compose.yaml       # Local database setup
├── api-stack.yaml           # AWS SAM template (API)
├── database-stack.yaml      # AWS SAM template (Database)
└── .env                     # Environment variables
```

## Development Workflow

### Making Changes

1. Edit code in the `app/` directory
2. The server will auto-reload (using `--reload` flag)
3. Test changes via Swagger UI or your API client

### Installing New Dependencies

```bash
pip install <package-name>
pip freeze > app/requirements.txt
```

## Testing

### Manual Testing with cURL

**Health Check (No Auth):**
```bash
curl http://localhost:8000/health
```

**Get Members by Name (With Auth):**
```bash
curl http://localhost:8000/members?firstName=John \
  -H "X-API-Key: dev-api-key-12345"
```

**Create Member (With Auth):**
```bash
curl -X POST http://localhost:8000/members \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-api-key-12345" \
  -d '{
    "firstName": "Jane",
    "lastName": "Doe",
    "email": "jane.doe@example.com",
    "phone": 91234567,
    "age": 25,
    "isEmployee": false
  }'
```

**Get Member by ID (With Auth):**
```bash
curl http://localhost:8000/members/{member-id} \
  -H "X-API-Key: dev-api-key-12345"
```

## Troubleshooting

### Port Already in Use

If port 5432 or 8000 is already in use:

**Change PostgreSQL port in [docker-compose.yaml](docker-compose.yaml):**
```yaml
ports:
  - "5433:5432"  # Use 5433 instead
```

Update `DB_PORT` in [.env](.env) accordingly.

**Change API port:**
```bash
uvicorn main:app --reload --port 8001
```

### Database Connection Issues

1. Verify PostgreSQL is running:
   ```bash
   docker ps
   ```

2. Check logs:
   ```bash
   docker logs members-postgres
   ```

3. Verify environment variables in [.env](.env) match [docker-compose.yaml](docker-compose.yaml)

### Module Import Errors

Ensure you're in the `app/` directory when running the server:
```bash
cd app
uvicorn main:app --reload
```

### Virtual Environment Not Activated

You should see `(venv)` in your terminal prompt. If not, activate it:
```bash
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\Activate.ps1  # Windows
```

## Stopping the Development Environment

### Stop API Server
Press `Ctrl+C` in the terminal running uvicorn

### Stop Database
```bash
docker-compose down
```

### Stop and Remove Data
```bash
docker-compose down -v
```

## Next Steps

- See [deploy_stack.md](deploy_stack.md) for AWS deployment
- Review [member.spec.yaml](member.spec.yaml) for API specification
- Check [README.md](README.md) for production deployment details

## Notes

- The local environment automatically creates database tables on startup
- Sample data is seeded automatically if the database is empty (see [seed.py](app/seed.py))
- **Local authentication uses API keys** (via `X-API-Key` header)
- **Production uses AWS Cognito OAuth 2.0** (Bearer token authentication)
- The authentication system automatically detects the environment and uses the appropriate method
- Email notifications require AWS SES configuration (not available locally)
