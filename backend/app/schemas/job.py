from datetime import datetime

from pydantic import BaseModel


class JobStageRead(BaseModel):
    id: int
    name: str
    position: int

    model_config = {"from_attributes": True}


class JobCreate(BaseModel):
    title: str
    company: str
    location: str
    department: str | None = None
    employment_type: str = "Full-time"
    status: str = "open"
    description: str
    requirements: str | None = None
    min_salary: float | None = None
    max_salary: float | None = None
    stage_names: list[str] | None = None


class JobUpdate(BaseModel):
    title: str | None = None
    company: str | None = None
    location: str | None = None
    department: str | None = None
    employment_type: str | None = None
    status: str | None = None
    description: str | None = None
    requirements: str | None = None
    min_salary: float | None = None
    max_salary: float | None = None
    stage_names: list[str] | None = None


class JobRead(BaseModel):
    id: int
    title: str
    company: str
    location: str
    department: str | None
    employment_type: str
    status: str
    description: str
    requirements: str | None
    min_salary: float | None
    max_salary: float | None
    created_at: datetime
    stages: list[JobStageRead]
    applications_count: int

    model_config = {"from_attributes": True}
