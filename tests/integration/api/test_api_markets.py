from fastapi.testclient import TestClient

from icon_stats.config import config


def test_api_get_markets(client: TestClient):
    response = client.get(f"{config.API_REST_PREFIX}/stats/exchanges/legacy")
    assert response.status_code == 200
    assert response.json()['data']['marketCap'] > 10000000


def test_api_get_prep_error(client: TestClient):
    # TODO
    response = client.get(
        f"{config.API_REST_PREFIX}/stats"
    )
    assert response.status_code == 204
