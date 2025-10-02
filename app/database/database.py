from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
import json
import boto3

load_dotenv()

def get_database_credentials():
    """Get database credentials from AWS Secrets Manager (Lambda) or environment variables (local dev)"""
    # Check if running in AWS Lambda
    if os.getenv("AWS_LAMBDA_FUNCTION_NAME"):
        # Running in AWS Lambda - use Secrets Manager
        secret_arn = os.environ.get("DB_SECRET_ARN")
        if not secret_arn:
            raise ValueError("DB_SECRET_ARN environment variable not found")

        secrets_client = boto3.client('secretsmanager')
        try:
            response = secrets_client.get_secret_value(SecretId=secret_arn)
            secret = json.loads(response['SecretString'])
            return {
                'username': secret['username'],
                'password': secret['password'],
                'host': os.environ.get("DB_HOST"),
                'port': os.environ.get("DB_PORT"),
                'dbname': os.environ.get("DB_NAME")
            }
        except Exception as e:
            raise Exception(f"Failed to retrieve database credentials from Secrets Manager: {e}")
    else:
        # Running locally - use environment variables from .env
        return {
            'username': os.environ.get("DB_USER"),
            'password': os.environ.get("DB_PASSWORD"),
            'host': os.environ.get("DB_HOST"),
            'port': os.environ.get("DB_PORT"),
            'dbname': os.environ.get("DB_NAME")
        }

# Get database credentials
db_creds = get_database_credentials()
DATABASE_URL = f"postgresql+psycopg2://{db_creds['username']}:{db_creds['password']}@{db_creds['host']}:{db_creds['port']}/{db_creds['dbname']}"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()