from sqlalchemy.orm import Session
from app.models import Member, Category, TaskType, Setting

INITIAL_MEMBERS = ["田中", "佐藤", "鈴木"]
INITIAL_CATEGORIES = ["定常保守", "突発保守", "依頼対応"]
INITIAL_TASK_TYPES = ["問い合わせ対応", "バグ修正", "定期メンテナンス", "ドキュメント更新", "その他"]
INITIAL_SETTINGS = {
    "default_week_end": "3",  # 0=Mon,...3=Thu,...4=Fri
    "master_password": "admin",  # 初期パスワード
}


def seed_members(db: Session) -> None:
    if db.query(Member).count() > 0:
        return
    for name in INITIAL_MEMBERS:
        db.add(Member(name=name))
    db.commit()


def seed_categories(db: Session) -> None:
    if db.query(Category).count() > 0:
        return
    for i, name in enumerate(INITIAL_CATEGORIES):
        db.add(Category(name=name, sort_order=i))
    db.commit()


def seed_task_types(db: Session) -> None:
    if db.query(TaskType).count() > 0:
        return
    for i, name in enumerate(INITIAL_TASK_TYPES):
        db.add(TaskType(name=name, sort_order=i))
    db.commit()


def seed_settings(db: Session) -> None:
    for key, value in INITIAL_SETTINGS.items():
        if not db.query(Setting).get(key):
            db.add(Setting(key=key, value=value))
    db.commit()


def seed_all(db: Session) -> None:
    seed_members(db)
    seed_categories(db)
    seed_task_types(db)
    seed_settings(db)
