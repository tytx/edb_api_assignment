
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional
from database.database import get_db
from models.member_model import MemberCreate, Member, MembersResponse, ErrorResponse
from services.member_service import create_member, get_members, get_member_by_id
from utils.auth import verify_api_key
import jwt
import os

router = APIRouter()

def get_cognito_user_email(request: Request) -> Optional[str]:
    """Extract email from Cognito JWT token"""
    try:
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return None

        token = auth_header.replace('Bearer ', '')
        # Decode without verification (API Gateway already verified it)
        decoded = jwt.decode(token, options={"verify_signature": False})
        return decoded.get('email')
    except Exception as e:
        print(f"Failed to extract email from token: {str(e)}")
        return None

@router.post("/members", response_model=Member, status_code=201)
def create_member_route(
    member: MemberCreate,
    request: Request,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    # Extract Cognito user email from JWT token
    cognito_email = get_cognito_user_email(request)
    db_member = create_member(db, member, cognito_email)
    return Member(**db_member.__dict__)

@router.get("/members", response_model=MembersResponse, responses={404: {"model": ErrorResponse}})
def list_members_route(
    firstName: Optional[str] = None,
    lastName: Optional[str] = None,
    db: Session = Depends(get_db),
    request: Request = None,
    api_key: str = Depends(verify_api_key)
):
    allowed = {"firstName", "lastName"}
    for param in request.query_params:
        if param not in allowed:
            raise HTTPException(status_code=400, detail=f"Invalid query parameter: {param}")

    results = get_members(db, firstName, lastName)
    
    if not results:
        raise HTTPException(status_code=404, detail="No members found for the given query.")
    members = [Member(**member.__dict__) for member in results]
    return MembersResponse(message="Members retrieved successfully", members=members)

@router.get("/members/{id}", response_model=Member)
def get_member_route(
    id: UUID,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    db_member = get_member_by_id(db, id)
    if not db_member:
        raise HTTPException(status_code=404, detail="Member not found")
    return Member(**db_member.__dict__)