from datetime import datetime
from pydantic import BaseModel


class MemberOut(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class TaskCreate(BaseModel):
    name: str
    category: str
    type: str = ""
    registered_by: str


class TaskUpdate(BaseModel):
    name: str
    category: str
    type: str = ""


class TaskOut(BaseModel):
    id: int
    name: str
    category: str
    type: str | None
    registered_by: str
    created_at: datetime

    model_config = {"from_attributes": True}


class SummaryOut(BaseModel):
    total: int
    by_category: dict[str, int]


class MasterItemOut(BaseModel):
    id: int
    name: str
    sort_order: int

    model_config = {"from_attributes": True}


class MasterItemCreate(BaseModel):
    name: str


class MasterItemReorder(BaseModel):
    ids: list[int]


class SettingOut(BaseModel):
    key: str
    value: str

    model_config = {"from_attributes": True}


class SettingUpdate(BaseModel):
    value: str
