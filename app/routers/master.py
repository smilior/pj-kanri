from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Category, TaskType, Setting, Member
from app.schemas import (
    MasterItemOut, MasterItemCreate, MasterItemReorder,
    SettingOut, SettingUpdate, MemberOut,
)

router = APIRouter(prefix="/api/master", tags=["master"])


# --- Categories ---

@router.get("/categories", response_model=list[MasterItemOut])
def list_categories(db: Session = Depends(get_db)):
    return db.query(Category).order_by(Category.sort_order).all()


@router.post("/categories", response_model=MasterItemOut, status_code=201)
def create_category(body: MasterItemCreate, db: Session = Depends(get_db)):
    max_order = db.query(Category).count()
    item = Category(name=body.name, sort_order=max_order)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/categories/{item_id}", status_code=204)
def delete_category(item_id: int, db: Session = Depends(get_db)):
    item = db.query(Category).get(item_id)
    if not item:
        raise HTTPException(404, "Not found")
    db.delete(item)
    db.commit()


@router.put("/categories/reorder", response_model=list[MasterItemOut])
def reorder_categories(body: MasterItemReorder, db: Session = Depends(get_db)):
    for i, item_id in enumerate(body.ids):
        item = db.query(Category).get(item_id)
        if item:
            item.sort_order = i
    db.commit()
    return db.query(Category).order_by(Category.sort_order).all()


# --- Task Types ---

@router.get("/task-types", response_model=list[MasterItemOut])
def list_task_types(db: Session = Depends(get_db)):
    return db.query(TaskType).order_by(TaskType.sort_order).all()


@router.post("/task-types", response_model=MasterItemOut, status_code=201)
def create_task_type(body: MasterItemCreate, db: Session = Depends(get_db)):
    max_order = db.query(TaskType).count()
    item = TaskType(name=body.name, sort_order=max_order)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/task-types/{item_id}", status_code=204)
def delete_task_type(item_id: int, db: Session = Depends(get_db)):
    item = db.query(TaskType).get(item_id)
    if not item:
        raise HTTPException(404, "Not found")
    db.delete(item)
    db.commit()


@router.put("/task-types/reorder", response_model=list[MasterItemOut])
def reorder_task_types(body: MasterItemReorder, db: Session = Depends(get_db)):
    for i, item_id in enumerate(body.ids):
        item = db.query(TaskType).get(item_id)
        if item:
            item.sort_order = i
    db.commit()
    return db.query(TaskType).order_by(TaskType.sort_order).all()


# --- Members ---

@router.get("/members", response_model=list[MemberOut])
def list_members(db: Session = Depends(get_db)):
    return db.query(Member).order_by(Member.id).all()


@router.post("/members", response_model=MemberOut, status_code=201)
def create_member(body: MasterItemCreate, db: Session = Depends(get_db)):
    item = Member(name=body.name)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/members/{item_id}", status_code=204)
def delete_member(item_id: int, db: Session = Depends(get_db)):
    item = db.query(Member).get(item_id)
    if not item:
        raise HTTPException(404, "Not found")
    db.delete(item)
    db.commit()


# --- Settings ---

@router.get("/settings", response_model=list[SettingOut])
def list_settings(db: Session = Depends(get_db)):
    return db.query(Setting).all()


@router.put("/settings/{key}", response_model=SettingOut)
def update_setting(key: str, body: SettingUpdate, db: Session = Depends(get_db)):
    setting = db.query(Setting).get(key)
    if not setting:
        setting = Setting(key=key, value=body.value)
        db.add(setting)
    else:
        setting.value = body.value
    db.commit()
    db.refresh(setting)
    return setting
