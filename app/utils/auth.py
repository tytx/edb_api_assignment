import os
from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

# API Key header scheme for local development
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def get_api_key() -> str:
    """Get API key from environment variables"""
    api_key = os.getenv("API_KEY")
    if not api_key:
        return "dev-api-key-12345"
    return api_key

async def verify_api_key(api_key: str = Security(api_key_header)):
    """
    Verify API key for local development
    This dependency is only used when not running in AWS Lambda
    """
    if os.getenv("AWS_LAMBDA_FUNCTION_NAME"):
        return None
    expected_key = get_api_key()

    if api_key is None or api_key != expected_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    return api_key
