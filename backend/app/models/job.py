from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.job_stage import JobStage
    from app.models.application import Application


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255))
    company: Mapped[str] = mapped_column(String(255))
    location: Mapped[str] = mapped_column(String(255))
    department: Mapped[str | None] = mapped_column(String(255), nullable=True)
    employment_type: Mapped[str] = mapped_column(String(100), default="Full-time")
    status: Mapped[str] = mapped_column(String(50), default="open")
    description: Mapped[str] = mapped_column(String)
    requirements: Mapped[str | None] = mapped_column(String, nullable=True)
    min_salary: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    max_salary: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    created_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    creator: Mapped[Optional["User"]] = relationship(back_populates="jobs")
    stages: Mapped[list["JobStage"]] = relationship(back_populates="job", cascade="all, delete-orphan", order_by="JobStage.position")
    applications: Mapped[list["Application"]] = relationship(back_populates="job", cascade="all, delete-orphan")
