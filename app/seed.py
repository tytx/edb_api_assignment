from database.database import SessionLocal
from database.db_model import Member
from datetime import datetime
import uuid

# mock sample data for database seed (testing)
def seed_sample_member():
    db = SessionLocal()
    if db.query(Member).count() == 0:
        sample_member = Member(
            id=uuid.UUID("d2e2c905-0e57-410d-bd31-a99deed4d39e"),
            firstName="John",
            lastName="Tan",
            email="johntan@gmail.com",
            phone="91234567",
            age=30,
            isEmployee=True,
            createdAt=datetime.fromisoformat("2025-09-27T06:42:55.811443")
        )
        db.add(sample_member)
        db.commit()
        print("Sample member added.")
    else:
        print("Database already has members.")
    db.close()