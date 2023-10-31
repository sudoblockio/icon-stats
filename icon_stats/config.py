import os
from pydantic_settings import BaseSettings, SettingsConfigDict

from pydantic import Field

from icon_stats.db_config import DbConfigs
from icon_stats.clients.configs import CmcClientConfig

class Settings(BaseSettings):
    # General
    NAME: str = "stats"
    VERSION: str = "v0.1.2"  # x-release-please-version
    NETWORK_NAME: str = "mainnet"

    # Exchanges
    cmc: CmcClientConfig = Field(default_factory=CmcClientConfig)

    # Enablers - Allows you to disable part of the service
    ENABLE_API: bool = True
    ENABLE_CRON: bool = True
    ENABLE_STREAMING: bool = True

    # API
    API_PORT: int = 8000
    API_REST_PREFIX: str = "/api/v1"
    API_DOCS_PREFIX: str = "/api/v1/stats/docs"
    API_MAX_PAGE_SIZE: int = 100

    CORS_ALLOW_ORIGINS: str = "*"
    CORS_ALLOW_CREDENTIALS: bool = False
    CORS_ALLOW_METHODS: str = "GET,POST,HEAD,OPTIONS"
    CORS_ALLOW_HEADERS: str = ""
    CORS_EXPOSE_HEADERS: str = "x-total-count"

    # Cron
    CRON_SLEEP_SEC: int = 600

    # Monitoring
    METRICS_PORT: int = 9400
    METRICS_ADDRESS: str = "localhost"
    METRICS_PREFIX: str = "/metrics"

    # Health
    HEALTH_PORT: int = 8180
    HEALTH_PREFIX: str = "/heath"
    HEALTH_POLLING_INTERVAL: int = 60

    # Endpoints
    ICON_NODE_URL: str = "https://api.icon.community/api/v3"
    COMMUNITY_API_ENDPOINT: str = "https://tracker.icon.community"

    # DB
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "changeme"
    POSTGRES_SERVER: str = "127.0.0.1"
    POSTGRES_PORT: str = "5432"
    POSTGRES_DATABASE: str = "postgres"

    db: DbConfigs = Field(default_factory=DbConfigs)

    # Kafka
    KAFKA_BROKER_URL: str = "localhost:29092"
    CONSUMER_IS_TAIL: bool = False
    CONSUMER_GROUP: str = "stats"
    CONSUMER_TOPIC_BLOCKS: str = "blocks"
    CONSUMER_AUTO_OFFSET_RESET: str = "earliest"
    JOB_ID: str | None = None

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_TO_FILE: bool = False
    LOG_FILE_NAME: str = "stats.log"
    LOG_FORMAT: str = "string"  # or "json"
    LOG_INDENT: int = 4
    LOG_INCLUDE_FIELDS: list[str] = ["timestamp", "message"]
    LOG_EXCLUDE_FIELDS: list[str] = []

    model_config = SettingsConfigDict(
        case_sensitive=False,
    )



if os.environ.get("ENV_FILE", False):
    config = Settings(_env_file=os.environ.get("ENV_FILE"))
else:
    config = Settings()
