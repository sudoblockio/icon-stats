import pytest
import os


def test_settings():
    from icon_stats.config import config

    assert config.db.contracts.user == "postgres"
    assert config.db.transformer.user == "postgres"
    assert config.db.governance.user == "postgres"
    assert config.cmc.cmc_endpoint.startswith("https")


@pytest.mark.parametrize(
    "env_var",
    [
        'DB_CONTRACTS_USER',
        'CMC_ENDPOINT',
    ]
)
def test_settings_with_env_var_db(env_var):
    os.environ[env_var] = 'foo'
    from icon_stats.config import config
    os.environ.pop(env_var)

    assert config.db.contracts.user == "foo"
