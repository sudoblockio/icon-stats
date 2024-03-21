from multiprocessing.pool import ThreadPool
import uvicorn
from fastapi import FastAPI
from fastapi_health import health
from prometheus_client import start_http_server
from starlette.middleware.cors import CORSMiddleware
from brotli_asgi import BrotliMiddleware

from icon_stats.api.health import is_database_online
from icon_stats.api.v1.router import api_router
from icon_stats.config import config
from icon_stats.log import logger

description = """Ecosystem wide statistics."""

tags_metadata = [
    {"name": "icon-stats", "description": description, },
]

app = FastAPI(
    title="ICON Statistics Service",
    description=description,
    version=config.VERSION,
    openapi_tags=tags_metadata,
    openapi_url=f"{config.API_DOCS_PREFIX}/openapi.json",
    docs_url=f"{config.API_DOCS_PREFIX}",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in config.CORS_ALLOW_ORIGINS.split(',')],
    allow_credentials=config.CORS_ALLOW_CREDENTIALS,
    allow_methods=[method.strip() for method in config.CORS_ALLOW_METHODS.split(',')],
    allow_headers=[header.strip() for header in config.CORS_ALLOW_HEADERS.split(',')],
    expose_headers=[header.strip() for header in
                    config.CORS_EXPOSE_HEADERS.split(',')],
)

app.add_middleware(
    BrotliMiddleware,
    quality=8,
)


@app.on_event("startup")
async def setup():
    logger.info("Starting metrics server.")
    metrics_pool = ThreadPool(1)
    metrics_pool.apply_async(
        start_http_server,
        (config.METRICS_PORT, config.METRICS_ADDRESS),
    )

    # logger.info("Starting cache loop...")
    # pool = ThreadPool(1)
    # pool.apply_async(cache_cron)


logger.info("Starting application...")
app.include_router(api_router, prefix=config.API_REST_PREFIX)
app.add_api_route(config.HEALTH_PREFIX, health([is_database_online]))

if __name__ == "__main__":
    uvicorn.run(
        "main_api:app",
        host="0.0.0.0",
        port=config.API_PORT,
        log_level="info",
        workers=1,
    )
