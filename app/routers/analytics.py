from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import Task, Setting

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


def _get_week_end(db: Session) -> int:
    s = db.query(Setting).get("default_week_end")
    return int(s.value) if s else 3


def _get_period_range(period: str | None, week_end: int):
    if not period:
        return None, None
    now = datetime.now(timezone.utc)
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    if period == "today":
        return today, today + timedelta(days=1)
    if period in ("this-week", "last-week"):
        weekday = today.weekday()
        diff = (weekday - week_end) % 7
        end_date = today - timedelta(days=diff)
        if period == "last-week":
            end_date = end_date - timedelta(days=7)
        return end_date - timedelta(days=6), end_date + timedelta(days=1)
    if period == "this-month":
        start = today.replace(day=1)
        end = start.replace(month=start.month + 1) if start.month < 12 else start.replace(year=start.year + 1, month=1)
        return start, end
    return None, None


def _filtered_query(db: Session, category: str | None, period: str | None):
    q = db.query(Task)
    if category:
        q = q.filter(Task.category == category)
    we = _get_week_end(db)
    start, end = _get_period_range(period, we)
    if start and end:
        q = q.filter(Task.created_at >= start, Task.created_at < end)
    return q


@router.get("/weekly-trend")
def weekly_trend(
    weeks: int = Query(8, ge=1, le=52),
    category: str | None = Query(None),
    db: Session = Depends(get_db),
):
    we = _get_week_end(db)
    now = datetime.now(timezone.utc)
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    weekday = today.weekday()
    diff = (weekday - we) % 7
    current_end = today - timedelta(days=diff) + timedelta(days=1)

    result = []
    for i in range(weeks - 1, -1, -1):
        end = current_end - timedelta(weeks=i)
        start = end - timedelta(days=7)
        q = db.query(Task).filter(Task.created_at >= start, Task.created_at < end)
        if category:
            q = q.filter(Task.category == category)
        tasks = q.all()
        by_cat = {}
        for t in tasks:
            by_cat[t.category] = by_cat.get(t.category, 0) + 1
        result.append({
            "label": f"{start.month}/{start.day}~",
            "start": start.isoformat(),
            "end": end.isoformat(),
            "total": len(tasks),
            "by_category": by_cat,
        })
    return result


@router.get("/by-category")
def by_category(
    category: str | None = Query(None),
    period: str | None = Query(None),
    db: Session = Depends(get_db),
):
    tasks = _filtered_query(db, category, period).all()
    result = {}
    for t in tasks:
        result[t.category] = result.get(t.category, 0) + 1
    return result


@router.get("/by-type")
def by_type(
    category: str | None = Query(None),
    period: str | None = Query(None),
    db: Session = Depends(get_db),
):
    tasks = _filtered_query(db, category, period).all()
    result = {}
    for t in tasks:
        key = t.type or "未設定"
        result[key] = result.get(key, 0) + 1
    return dict(sorted(result.items(), key=lambda x: x[1], reverse=True))


@router.get("/by-member")
def by_member(
    category: str | None = Query(None),
    period: str | None = Query(None),
    db: Session = Depends(get_db),
):
    tasks = _filtered_query(db, category, period).all()
    result = {}
    for t in tasks:
        if t.registered_by not in result:
            result[t.registered_by] = {"total": 0}
        result[t.registered_by]["total"] += 1
        result[t.registered_by][t.category] = result[t.registered_by].get(t.category, 0) + 1
    return dict(sorted(result.items(), key=lambda x: x[1]["total"], reverse=True))


@router.get("/category-type-matrix")
def category_type_matrix(
    category: str | None = Query(None),
    period: str | None = Query(None),
    db: Session = Depends(get_db),
):
    tasks = _filtered_query(db, category, period).all()
    categories = sorted(set(t.category for t in tasks)) if tasks else []
    types = sorted(set(t.type or "未設定" for t in tasks)) if tasks else []
    matrix = {c: {ty: 0 for ty in types} for c in categories}
    for t in tasks:
        matrix[t.category][t.type or "未設定"] += 1
    return {"categories": categories, "types": types, "matrix": matrix}


@router.get("/repeat-tasks")
def repeat_tasks(
    category: str | None = Query(None),
    period: str | None = Query(None),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    q = _filtered_query(db, category, period).subquery()
    rows = (
        db.query(q.c.name, func.count(q.c.id).label("count"), func.max(q.c.created_at).label("last_at"))
        .group_by(q.c.name)
        .having(func.count(q.c.id) >= 2)
        .order_by(func.count(q.c.id).desc())
        .limit(limit)
        .all()
    )
    return [{"name": r.name, "count": r.count, "last_at": r.last_at.isoformat() if r.last_at else None} for r in rows]
