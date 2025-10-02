from mangum import Mangum
from main import app

# Lambda handler for FastAPI with optimizations
lambda_handler = Mangum(
    app,
    lifespan="off",  # Disable lifespan events for Lambda
    text_mime_types=["application/json", "application/x-amz-json-1.0"]
)