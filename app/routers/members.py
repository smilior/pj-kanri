from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Member
from app.schemas import MemberOut

router = APIRouter(prefix="/api/members", tags=["members"])


@router.get("", response_model=list[MemberOut])
def list_members(db: Session = Depends(get_db)):
    return db.query(Member).order_by(Member.id).all()
