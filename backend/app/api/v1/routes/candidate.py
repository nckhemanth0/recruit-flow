from pathlib import Path
from uuid import uuid4

import httpx
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import require_role
from app.db.session import get_db
from app.models.application import Application
from app.models.job import Job
from app.models.job_stage import JobStage
from app.schemas.application import ApplicationRead
from app.schemas.job import JobStageRead
from app.schemas.user import UserProfileUpdate, UserRead

router = APIRouter(prefix="/candidate", tags=["candidate"])


def serialize_application(application: Application) -> ApplicationRead:
    stage = application.stage
    stage_payload = JobStageRead.model_validate(stage) if stage else None
    return ApplicationRead(
        id=application.id,
        status=application.status,
        resume_path=application.resume_path,
        cover_letter=application.cover_letter,
        created_at=application.created_at,
        updated_at=application.updated_at,
        stage=stage_payload,
        job_id=application.job.id,
        job_title=application.job.title,
        candidate=UserRead.model_validate(application.candidate),
        notes=[],
    )


@router.get("/profile", response_model=UserRead)
def get_profile(current_user=Depends(require_role(["candidate"]))) -> UserRead:
    return UserRead.model_validate(current_user)


@router.patch("/profile", response_model=UserRead)
def update_profile(payload: UserProfileUpdate, db: Session = Depends(get_db), current_user=Depends(require_role(["candidate"]))) -> UserRead:
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(current_user, key, value)
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return UserRead.model_validate(current_user)


@router.get("/applications", response_model=list[ApplicationRead])
def list_applications(db: Session = Depends(get_db), current_user=Depends(require_role(["candidate"]))) -> list[ApplicationRead]:
    applications = (
        db.query(Application)
        .filter(Application.candidate_id == current_user.id)
        .order_by(Application.created_at.desc())
        .all()
    )
    return [serialize_application(app) for app in applications]


@router.post("/resume/autofill")
async def autofill_resume(
    resume: UploadFile = File(...),
    current_user=Depends(require_role(["candidate"])),
) -> dict:
    if not settings.resume_parser_url or not settings.resume_parser_api_key:
        raise HTTPException(status_code=503, detail="Resume parsing service not configured")

    files = {
        "resume": (resume.filename or "resume", await resume.read(), resume.content_type or "application/octet-stream"),
    }
    headers = {"Authorization": f"Bearer {settings.resume_parser_api_key}"}

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(settings.resume_parser_url, headers=headers, files=files)
            if response.status_code >= 400:
                raise HTTPException(status_code=response.status_code, detail=response.text or "Resume parsing failed")
            payload = response.json()
    except httpx.TimeoutException as exc:
        raise HTTPException(status_code=504, detail="Resume parsing service timed out") from exc
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail="Resume parsing service unavailable") from exc

    return payload


@router.post("/applications", response_model=ApplicationRead)
def apply_for_job(
    job_id: int = Form(...),
    cover_letter: str | None = Form(None),
    resume: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["candidate"])),
) -> ApplicationRead:
    job = db.get(Job, job_id)
    if not job or job.status != "open":
        raise HTTPException(status_code=404, detail="Job not available")
    existing = (
        db.query(Application)
        .filter(Application.candidate_id == current_user.id, Application.job_id == job.id)
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Already applied")
    if job.stages:
        stage = sorted(job.stages, key=lambda s: s.position)[0]
    else:
        stage = JobStage(job_id=job.id, name="Applied", position=1)
        db.add(stage)
        db.flush()
    resume_path = None
    if resume:
        uploads_dir = Path(settings.resume_upload_dir)
        uploads_dir.mkdir(parents=True, exist_ok=True)
        original_name = Path(resume.filename or "resume.pdf").name.replace(" ", "_")
        filename = f"{current_user.id}_{job.id}_{uuid4().hex}_{original_name}"
        file_path = uploads_dir / filename
        with open(file_path, "wb") as buffer:
            buffer.write(resume.file.read())
        resume_path = f"/uploads/{uploads_dir.name}/{filename}"
    application = Application(
        candidate_id=current_user.id,
        job_id=job.id,
        stage_id=stage.id,
        cover_letter=cover_letter,
        resume_path=resume_path,
    )
    db.add(application)
    db.commit()
    db.refresh(application)
    return serialize_application(application)
