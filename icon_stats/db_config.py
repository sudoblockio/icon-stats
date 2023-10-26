"""
This being the stats service is supposed to connect to many DBs and summarize their
stats. As such, we need to be able to bring in the connections from multiple different
DBs. Thus this hacky config is allowing us to inject DB creds for all those DBs.
"""
# from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseSettings
from pydantic import Field


class BaseDbConfig(BaseSettings):
    user: str = "postgres"
    password: str = "changeme"
    server: str = "127.0.0.1"
    port: str = "5432"
    database: str = "postgres"
    schema_: str = Field("public", alias="schema")


class StatsDbConfig(BaseDbConfig):
    schema_: str = Field("stats", alias="schema")

    # model_config = SettingsConfigDict(
    #     env_prefix='db_stats_',
    #     case_sensitive=False,
    # )
    class Config:
        env_prefix='db_stats_',
        case_sensitive=False,

class TransformerDbConfig(BaseDbConfig):
    # model_config = SettingsConfigDict(
    #     env_prefix='db_transformer_',
    #     case_sensitive=False,
    # )
    pass


class ContractsDbConfig(BaseDbConfig):
    # model_config = SettingsConfigDict(
    #     env_prefix='db_contracts_',
    #     case_sensitive=False,
    # )
    pass


class GovernanceDbConfig(BaseDbConfig):
    # model_config = SettingsConfigDict(
    #     env_prefix='db_governance_',
    #     case_sensitive=False,
    # )
    pass


class DbConfigs(BaseSettings):
    stats: StatsDbConfig = Field(default_factory=StatsDbConfig)
    # transformer: TransformerDbConfig = Field(default_factory=TransformerDbConfig)
    # contracts: ContractsDbConfig = Field(default_factory=ContractsDbConfig)
    # governance: GovernanceDbConfig = Field(default_factory=GovernanceDbConfig)

    # model_config = SettingsConfigDict(
    #     # env_prefix='db_',
    #     case_sensitive=False,
    # )

    class Config:
        env_prefix='db_stats_',
        case_sensitive=False,
