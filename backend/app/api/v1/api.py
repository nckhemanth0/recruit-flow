from fastapi import APIRouter

from .routes import auth, candidate, health, public, recruiter

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth")
api_router.include_router(public.router)
api_router.include_router(candidate.router)
api_router.include_router(recruiter.router)
api_router.include_router(health.router, prefix="/health", tags=["health"])
