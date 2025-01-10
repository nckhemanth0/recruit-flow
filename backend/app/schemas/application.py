from datetime import datetime

from pydantic import BaseModel

from app.schemas.job import JobStageRead
from app.schemas.user import UserRead


class ApplicationCreate(BaseModel):
    job_id: int
    cover_letter: str | None = None


class ApplicationMove(BaseModel):
    stage_id: int


class ApplicationNoteCreate(BaseModel):
    body: str


class ApplicationNoteRead(BaseModel):
    id: int
    body: str
    created_at: datetime
    author_id: int | None
    author_name: str | None


class ApplicationRead(BaseModel):
    id: int
    status: str
    resume_path: str | None
    cover_letter: str | None
    created_at: datetime
    updated_at: datetime
    stage: JobStageRead | None
    job_id: int
    job_title: str
    candidate: UserRead
    notes: list[ApplicationNoteRead]

    model_config = {"from_attributes": True}
