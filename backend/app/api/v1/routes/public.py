from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.job import Job
from app.schemas.job import JobRead, JobStageRead

router = APIRouter(tags=["public"])


@router.get("/jobs", response_model=list[JobRead])
def list_jobs(db: Session = Depends(get_db)) -> list[JobRead]:
    jobs = db.query(Job).filter(Job.status == "open").order_by(Job.created_at.desc()).all()
    result: list[JobRead] = []
    for job in jobs:
        result.append(
            JobRead(
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
                stages=[JobStageRead.model_validate(stage) for stage in job.stages],
                applications_count=len(job.applications),
            )
        )
    return result


@router.get("/jobs/{job_id}", response_model=JobRead)
def job_detail(job_id: int, db: Session = Depends(get_db)) -> JobRead:
    job = db.get(Job, job_id)
    if not job or job.status != "open":
        raise HTTPException(status_code=404, detail="Job not found")
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
        stages=[JobStageRead.model_validate(stage) for stage in job.stages],
        applications_count=len(job.applications),
    )
