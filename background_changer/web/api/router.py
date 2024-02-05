from fastapi.routing import APIRouter

from background_changer.web.api import change_bg, echo, monitoring

api_router = APIRouter()
api_router.include_router(monitoring.router)
# api_router.include_router(users.router)
api_router.include_router(echo.router, prefix="/echo", tags=["echo"])
api_router.include_router(change_bg.router, prefix="/change_bg", tags=["echo"])

# api_router.include_router(dummy.router, prefix="/dummy", tags=["dummy"])
# api_router.include_router(redis.router, prefix="/redis", tags=["redis"])
# api_router.include_router(rabbit.router, prefix="/rabbit", tags=["rabbit"])
