from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.database import engine, SessionLocal, Base
from app.models import Member, Task, Category, TaskType, Setting  # noqa: F401
from app.routers import members, tasks, master, analytics
from app.seed import seed_all


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_all(db)
    finally:
        db.close()
    yield


app = FastAPI(title="PJ案件外 作業管理", lifespan=lifespan)

app.include_router(members.router)
app.include_router(tasks.router)
app.include_router(master.router)
app.include_router(analytics.router)

app.mount("/", StaticFiles(directory="static", html=True), name="static")
