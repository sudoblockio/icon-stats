from fastapi import APIRouter

from icon_stats.api.v1.endpoints import exchanges_legacy, token_stats, openapi

api_router = APIRouter(prefix="/statistics")
api_router.include_router(token_stats.router)
api_router.include_router(exchanges_legacy.router)
api_router.include_router(openapi.router)
