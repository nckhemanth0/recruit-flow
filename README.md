# Recruit Flow

Recruit Flow is a lean Workday-style applicant tracking platform. Candidates can browse and apply for open roles, recruiters can publish jobs and manage pipelines, and everything runs on a FastAPI + Vue 3 stack.

## Project Layout

```
recruiting-application/
├── backend/        # FastAPI app with auth, jobs, candidates, recruiter APIs
├── frontend/       # Vue 3 + Tailwind single page app (public/candidate/recruiter views)
├── docker/         # Dockerfiles & helper scripts
├── docker-compose.yml
├── Makefile
└── docs/           # Step-by-step build notes
```

## Prerequisites

- Docker & Docker Compose (recommended path via `make up`)
- Node.js 20+ if you run the frontend manually
- Python 3.11+ if you run the backend manually

## Environment

Copy `.env.example` to `.env` in the project root. Values include database credentials, JWT secret, and the frontend API base URL.

## Run with Docker (default)

```bash
make up   # builds images and starts Postgres, FastAPI, Vue dev server, PgAdmin
make down # stops containers
```

Services:
- API: http://localhost:8000/api/v1
- Frontend: http://localhost:5173
- PgAdmin: http://localhost:5050

## Manual Development (optional)

Backend:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn app.main:app --app-dir backend --reload
```

Frontend:
```bash
cd frontend
npm install
npm run dev
```

## Key Features

- **Public careers site**: browse open roles, view job detail, see stage breakdown.
- **Candidate portal**: self-register, manage profile, upload resume, view application status.
- **Recruiter console**: create jobs with custom pipelines, view applicants per stage, drag-free stage selection, add hiring notes.
- **REST API**: JWT auth, role-based access, resume uploads stored on disk.

Use `/auth/register` to create candidate and recruiter accounts (set `role` to `candidate` or `recruiter`). Log in through the appropriate portal routes:

- Candidate login: http://localhost:5173/candidate/login
- Recruiter login: http://localhost:5173/recruiter/login

## Documentation

Build notes for this step live in `docs/steps/step-01-project-scaffold.md`.
