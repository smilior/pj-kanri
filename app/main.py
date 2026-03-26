from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.database import engine, SessionLocal, Base
from app.models import Member, Task  # noqa: F401 (ensure tables are registered)
from app.routers import members, tasks
from app.seed import seed_members


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_members(db)
    finally:
        db.close()
    yield


app = FastAPI(title="PJ案件外 作業管理", lifespan=lifespan)

app.include_router(members.router)
app.include_router(tasks.router)

app.mount("/", StaticFiles(directory="static", html=True), name="static")
