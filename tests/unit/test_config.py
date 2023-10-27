from icon_stats.config import config


def test_settings():
    assert config.db.contracts.user == "postgres"
    assert config.db.transformer.user == "postgres"
    assert config.db.governance.user == "postgres"
    assert config.cmc.endpoint.startswith("https")
