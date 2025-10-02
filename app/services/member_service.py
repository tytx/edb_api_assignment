from sqlalchemy.orm import Session
from uuid import UUID
from database.db_model import Member as MemberTable
from models.member_model import MemberCreate, Member
from services.notification_service import get_notification_service

def create_member(db: Session, member: MemberCreate, cognito_user_email: str = None):
    db_member = MemberTable(
        firstName=member.firstName,
        lastName=member.lastName,
        email=member.email,
        phone=member.phone,
        age=member.age,
        isEmployee=member.isEmployee
    )
    db.add(db_member)
    db.commit()
    db.refresh(db_member)

    # Send notification email (non-blocking - don't fail if email fails)
    try:
        member_obj = Member(**db_member.__dict__)
        notification_service = get_notification_service()
        notification_service.send_new_member_notification(member_obj, cognito_user_email)
    except Exception as e:
        print(f"Notification failed but member created successfully: {str(e)}")

    return db_member

def get_members(db: Session, first_name: str = None, last_name: str = None):
    query = db.query(MemberTable)
    if first_name:
        query = query.filter(MemberTable.firstName == first_name)
    if last_name:
        query = query.filter(MemberTable.lastName == last_name)
    results = query.all()
    return results

def get_member_by_id(db: Session, member_id: UUID):
    return db.query(MemberTable).filter(MemberTable.id == member_id).first()
