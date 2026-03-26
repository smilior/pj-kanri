from sqlalchemy.orm import Session
from app.models import Member

INITIAL_MEMBERS = ["田中", "佐藤", "鈴木"]


def seed_members(db: Session) -> None:
    if db.query(Member).count() > 0:
        return
    for name in INITIAL_MEMBERS:
        db.add(Member(name=name))
    db.commit()
