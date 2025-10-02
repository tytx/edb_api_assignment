import os
from fastapi import FastAPI
from routes import members

app = FastAPI(title="Membership API", version="1.0.0")

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "membership-api", "environment": "lambda" if os.getenv("AWS_LAMBDA_FUNCTION_NAME") else "local"}

app.include_router(members.router)

# Only create tables and seed data in LOCAL development env
if os.getenv("AWS_LAMBDA_FUNCTION_NAME") is None:
    try:
        from database.db_model import Base
        from database.database import engine
        from seed import seed_sample_member
        Base.metadata.create_all(bind=engine)
        seed_sample_member()
    except Exception as e:
        print(f"Database initialization failed: {e}")
else:
    # In Lambda, we need to ensure tables exist
    try:
        from database.db_model import Base
        from database.database import engine
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"Database connection failed in Lambda: {e}")


