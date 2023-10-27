from fastapi import APIRouter

from icon_stats.api.v1.endpoints import token_stats
from icon_stats.api.v1.endpoints import exchanges_legacy


api_router = APIRouter()
# api_router.include_router(token_stats.router)
api_router.include_router(exchanges_legacy.router)