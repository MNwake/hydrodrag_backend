from fastapi import APIRouter, Request

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("")
def health(request: Request):
    app = request.app.state.app
    db_status = app.db.health_check()

    return {
        "status": "ok" if db_status["status"] == "ok" else "degraded",
        "database": db_status,
    }