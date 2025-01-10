from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import require_role
from app.db.session import get_db
from app.models.application import Application
from app.models.application_note import ApplicationNote
from app.models.job import Job
from app.models.job_stage import JobStage
from app.schemas.application import ApplicationMove, ApplicationNoteCreate, ApplicationNoteRead, ApplicationRead
from app.schemas.job import JobCreate, JobRead, JobStageRead, JobUpdate
from app.schemas.user import UserRead

router = APIRouter(prefix="/recruiter", tags=["recruiter"])


def serialize_job(job: Job) -> JobRead:
    return JobRead(
        id=job.id,
        title=job.title,
        company=job.company,
        location=job.location,
        department=job.department,
        employment_type=job.employment_type,
        status=job.status,
        description=job.description,
        requirements=job.requirements,
        min_salary=float(job.min_salary) if job.min_salary is not None else None,
        max_salary=float(job.max_salary) if job.max_salary is not None else None,
        created_at=job.created_at,
        stages=[JobStageRead.model_validate(stage) for stage in sorted(job.stages, key=lambda s: s.position)],
        applications_count=len(job.applications),
    )


def serialize_application(application: Application) -> ApplicationRead:
    stage = application.stage
    notes = [
        ApplicationNoteRead(
            id=note.id,
            body=note.body,
            created_at=note.created_at,
            author_id=note.author_id,
            author_name=note.author.full_name if note.author else None,
        )
        for note in sorted(application.notes, key=lambda n: n.created_at)
    ]
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
        notes=notes,
    )


@router.get("/jobs", response_model=list[JobRead])
def list_jobs(db: Session = Depends(get_db), current_user=Depends(require_role(["recruiter", "admin"]))) -> list[JobRead]:
    jobs = db.query(Job).filter(Job.created_by_id == current_user.id).order_by(Job.created_at.desc()).all()
    return [serialize_job(job) for job in jobs]


@router.post("/jobs", response_model=JobRead, status_code=status.HTTP_201_CREATED)
def create_job(payload: JobCreate, db: Session = Depends(get_db), current_user=Depends(require_role(["recruiter", "admin"]))) -> JobRead:
    job = Job(
        title=payload.title,
        company=payload.company,
        location=payload.location,
        department=payload.department,
        employment_type=payload.employment_type,
        status=payload.status,
        description=payload.description,
        requirements=payload.requirements,
        min_salary=payload.min_salary,
        max_salary=payload.max_salary,
        created_by_id=current_user.id,
    )
    db.add(job)
    db.flush()
    stage_names = payload.stage_names or ["Applied", "Screening", "Interview", "Offer", "Hired"]
    for index, name in enumerate(stage_names, start=1):
        db.add(JobStage(job_id=job.id, name=name, position=index))
    db.commit()
    db.refresh(job)
    return serialize_job(job)


@router.get("/jobs/{job_id}")
def job_detail(job_id: int, db: Session = Depends(get_db), current_user=Depends(require_role(["recruiter", "admin"]))) -> dict:
    job = db.get(Job, job_id)
    if not job or job.created_by_id != current_user.id:
        raise HTTPException(status_code=404, detail="Job not found")
    applications = (
        db.query(Application)
        .filter(Application.job_id == job.id)
        .order_by(Application.created_at.desc())
        .all()
    )
    return {
        "job": serialize_job(job).model_dump(),
        "applications": [serialize_application(app).model_dump() for app in applications],
    }


@router.patch("/jobs/{job_id}", response_model=JobRead)
def update_job(job_id: int, payload: JobUpdate, db: Session = Depends(get_db), current_user=Depends(require_role(["recruiter", "admin"]))) -> JobRead:
    job = db.get(Job, job_id)
    if not job or job.created_by_id != current_user.id:
        raise HTTPException(status_code=404, detail="Job not found")
    data = payload.model_dump(exclude_unset=True)
    stage_names = data.pop("stage_names", None)
    for key, value in data.items():
        setattr(job, key, value)
    if stage_names is not None:
        db.query(JobStage).filter(JobStage.job_id == job.id).delete()
        for index, name in enumerate(stage_names, start=1):
            db.add(JobStage(job_id=job.id, name=name, position=index))
    db.add(job)
    db.commit()
    db.refresh(job)
    return serialize_job(job)


@router.post("/applications/{application_id}/move", response_model=ApplicationRead)
def move_application(application_id: int, payload: ApplicationMove, db: Session = Depends(get_db), current_user=Depends(require_role(["recruiter", "admin"]))) -> ApplicationRead:
    application = db.get(Application, application_id)
    if not application or application.job.created_by_id != current_user.id:
        raise HTTPException(status_code=404, detail="Application not found")
    stage = db.get(JobStage, payload.stage_id)
    if not stage or stage.job_id != application.job_id:
        raise HTTPException(status_code=400, detail="Invalid stage")
    application.stage_id = stage.id
    db.add(application)
    db.commit()
    db.refresh(application)
    return serialize_application(application)


@router.post("/applications/{application_id}/notes", response_model=ApplicationRead)
def add_note(application_id: int, payload: ApplicationNoteCreate, db: Session = Depends(get_db), current_user=Depends(require_role(["recruiter", "admin"]))) -> ApplicationRead:
    application = db.get(Application, application_id)
    if not application or application.job.created_by_id != current_user.id:
        raise HTTPException(status_code=404, detail="Application not found")
    note = ApplicationNote(application_id=application.id, author_id=current_user.id, body=payload.body)
    db.add(note)
    db.commit()
    db.refresh(application)
    return serialize_application(application)
