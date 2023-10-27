from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from icon_stats.config import config


def test_api_get_markets(db: Session, client: TestClient):
    response = client.get(f"{config.API_REST_PREFIX}/stats/exchanges/legacy")
    assert response.status_code == 200


def test_api_get_prep_error(db: Session, client: TestClient):
    # TODO
    response = client.get(
        f"{config.API_REST_PREFIX}/stats"
    )
    assert response.status_code == 204
