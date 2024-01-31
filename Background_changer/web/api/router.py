from fastapi.routing import APIRouter
from Background_changer.web.api import users
from Background_changer.db.models.users import api_users
from Background_changer.web.api import echo
from Background_changer.web.api import dummy
from Background_changer.web.api import redis
from Background_changer.web.api import rabbit
from Background_changer.web.api import monitoring

api_router = APIRouter()
api_router.include_router(monitoring.router)
api_router.include_router(users.router)
api_router.include_router(echo.router, prefix="/echo", tags=["echo"])
api_router.include_router(dummy.router, prefix="/dummy", tags=["dummy"])
api_router.include_router(redis.router, prefix="/redis", tags=["redis"])
api_router.include_router(rabbit.router, prefix="/rabbit", tags=["rabbit"])
