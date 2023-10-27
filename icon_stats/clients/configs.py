from pydantic_settings import BaseSettings, SettingsConfigDict

class BaseRestClientConfig(BaseSettings):
    endpoint: str
    retries: int = 0
    timeout: int = 2


class CmcClientConfig(BaseRestClientConfig):
    api_key: str = ""
    endpoint: str = "https://pro-api.coinmarketcap.com"

    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_prefix='cmc_',
    )
