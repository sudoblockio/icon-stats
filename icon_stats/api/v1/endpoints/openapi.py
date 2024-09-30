from datetime import datetime
from typing import Dict, Optional, Any, List
from fastapi import APIRouter
from icon_stats.config import config
from icon_stats.openapi.operations import FetchSchema, ResolveRefs, ValidateParams
from icon_stats.openapi.processor import OpenAPIProcessor

router = APIRouter()

_cache: Dict[str, Optional[Any]] = {
    "data": None,
    "last_updated": None,
    "title": "ICON"
}


@router.get("/openapi")
async def get_merged_openapi_spec() -> dict:
    """Combine the openapi specs from multiple data sources by using a cache."""
    now = datetime.now()
    if _cache["data"] is not None and _cache["last_updated"] is not None:
        elapsed_time = (now - _cache["last_updated"]).total_seconds()
        if elapsed_time < config.CACHE_DURATION:
            return _cache["data"]

    endpoints_suffixes = [
        'api/v1/docs/doc.json',
        'api/v1/governance/docs/openapi.json',
        'api/v1/contracts/docs/openapi.json',
        'api/v1/statistics/docs/openapi.json',
    ]

    additional_endpoints = [
        'https://balanced.icon.community/api/v1/docs/openapi.json',
    ]

    schema_urls = get_openapi_urls(endpoint_suffixes=endpoints_suffixes,base_url=config.OPENAPI_ENDPOINT_PREFIX) + additional_endpoints

    output =  get_merged_openapi(schema_urls=schema_urls)

    # Update the cache
    _cache["data"] = output
    _cache["last_updated"] = now

    return output

def get_openapi_urls(endpoint_suffixes: List[str],base_url:str) -> List[str]:
    return [f"{base_url}/{suffix}" for suffix in endpoint_suffixes]


def get_merged_openapi(schema_urls: List[str],title:str = _cache['title']) -> Dict:

    schema_processor = OpenAPIProcessor(
        fetch_schema=FetchSchema(),
        resolve_schema_refs=ResolveRefs(),
        validate_params=ValidateParams()
    )
    schemas = schema_processor.process(schema_urls=schema_urls,title=title)

    return schemas.model_dump(by_alias=True, exclude_none=True)






