import pytest
import os


def test_settings():
    from icon_stats.config import config

    assert config.db.contracts.user == "postgres"
    assert config.db.transformer.user == "postgres"
    assert config.db.governance.user == "postgres"
    assert config.cmc.endpoint.startswith("https")


def test_settings_with_env_var_db():
    # TODO: Fix this - it is working since conftest is grabbing the right values
    os.environ['DB_CONTRACTS_USER'] = 'foo'
    from icon_stats.config import config
    os.environ.pop('DB_CONTRACTS_USER')

    assert config.db.contracts.user == "foo"


@pytest.mark.no_config_override
def test_settings_with_env_var_cmc():
    # TODO: Fix this - it is working since conftest is grabbing the right values
    os.environ['CMC_API_KEY'] = 'foo'
    from icon_stats.config import config
    os.environ.pop('CMC_API_KEY')

    assert config.cmc.api_key == "foo"
