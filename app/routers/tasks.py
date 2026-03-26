from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Task
from app.schemas import TaskCreate, TaskUpdate, TaskOut, SummaryOut

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


def _get_period_range(period: str | None, week_end: int = 3):
    """week_end: 0=Monday, 1=Tuesday, ... 4=Friday (the closing day of the week)
    Range: (week_end - 6 days) to (week_end + 1 day), i.e. 7 days ending on week_end."""
    if not period:
        return None, None
    now = datetime.now(timezone.utc)
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    if period == "today":
        return today, today + timedelta(days=1)
    if period == "this-week":
        weekday = today.weekday()  # Monday=0
        # Find the most recent occurrence of week_end (including today)
        diff = (weekday - week_end) % 7
        end_date = today - timedelta(days=diff)
        start_date = end_date - timedelta(days=6)
        return start_date, end_date + timedelta(days=1)  # end is exclusive
    if period == "this-month":
        start = today.replace(day=1)
        if start.month == 12:
            end = start.replace(year=start.year + 1, month=1)
        else:
            end = start.replace(month=start.month + 1)
        return start, end
    return None, None


def _apply_filters(query, category: str | None, period: str | None, week_end: int = 3):
    if category:
        query = query.filter(Task.category == category)
    start, end = _get_period_range(period, week_end)
    if start and end:
        query = query.filter(Task.created_at >= start, Task.created_at < end)
    return query


@router.get("", response_model=list[TaskOut])
def list_tasks(
    category: str | None = Query(None),
    period: str | None = Query(None),
    week_end: int = Query(3, ge=0, le=4),
    db: Session = Depends(get_db),
):
    q = _apply_filters(db.query(Task), category, period, week_end)
    return q.order_by(Task.created_at.desc()).all()


@router.get("/summary", response_model=SummaryOut)
def get_summary(
    category: str | None = Query(None),
    period: str | None = Query(None),
    week_end: int = Query(3, ge=0, le=4),
    db: Session = Depends(get_db),
):
    tasks = _apply_filters(db.query(Task), category, period, week_end).all()
    return SummaryOut(
        total=len(tasks),
        routine=sum(1 for t in tasks if t.category == "定常保守"),
        adhoc=sum(1 for t in tasks if t.category == "突発保守"),
        request=sum(1 for t in tasks if t.category == "依頼対応"),
    )


@router.post("", response_model=TaskOut, status_code=201)
def create_task(body: TaskCreate, db: Session = Depends(get_db)):
    task = Task(
        name=body.name,
        category=body.category,
        type=body.type or None,
        registered_by=body.registered_by,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.put("/{task_id}", response_model=TaskOut)
def update_task(task_id: int, body: TaskUpdate, db: Session = Depends(get_db)):
    task = db.query(Task).get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.name = body.name
    task.category = body.category
    task.type = body.type or None
    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
