from fastapi import APIRouter

router = APIRouter()


@router.get("", summary="Application health check")
def read_health() -> dict[str, str]:
    return {"status": "ok"}
