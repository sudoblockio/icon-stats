from datetime import datetime

from fastapi import APIRouter

from icon_stats.config import config
from icon_stats.models.ecosystem import Ecosystem

router = APIRouter()

_cache = {
    "data": None,
    "last_updated": None
}


@router.get("/openapi")
async def get_merged_openapi_spec() -> list[Ecosystem]:
    """Combine the openapi specs from multiple data sources by using a cache."""
    now = datetime.now()
    if _cache["data"] is not None and _cache["last_updated"] is not None:
        elapsed_time = (now - _cache["last_updated"]).total_seconds()
        if elapsed_time < config.CACHE_DURATION:
            return _cache["data"]

    # TODO: This should call the merging function on a list of endpoints
    #
    endpoints_suffixes = [
        'api/v1/docs/doc.json',
        'api/v1/governance/docs/openapi.json',
        'api/v1/contracts/docs/openapi.json',
        'api/v1/statistics/docs/openapi.json',
    ]

    additional_endpoints = [
        'https://balanced.icon.community/api/v1/docs/openapi.json',
    ]

    endpoints = [
                    f"{config.OPENAPI_ENDPOINT_PREFIX}/{i}" for i in endpoints_suffixes
                ] + additional_endpoints

    # TODO: Can be async or sync. In prod these calls are made inside cluster so will be fast
    output = get_merged_openapi()

    # Update the cache
    _cache["data"] = output
    _cache["last_updated"] = now

    return output
