import pytest

from icon_stats.crons import (  # cmc_cryptocurrency_quotes_latest,
    application_stats,
    applications_refresh,
    contract_stats,
    token_stats,
)

# @pytest.mark.asyncio
# async def test_crons_run_cmc_cryptocurrency_quotes_latest():
#     await cmc_cryptocurrency_quotes_latest.run_cmc_cryptocurrency_quotes_latest()


@pytest.fixture
def app_fixture():
    return {
        "id": "example",
        "name": "",
        "description": "",
        "url": "",
        "logo": "",
        "contracts": [
            "cx28b2ec885b50c8a93da752f2d0467a67127a70e8",
        ],
    }


@pytest.fixture
def token_fixture():
    return {
        "id": "example token",
        "name": "crown",
        "symbol": "",
        "contract": "cx28b2ec885b50c8a93da752f2d0467a67127a70e8",
    }


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "cron",
    [
        applications_refresh.run_applications_refresh,
        contract_stats.run_contract_stats,
        token_stats.run_token_stats,
        application_stats.run_application_stats,
    ],
)
async def test_crons(cron, mocker, app_fixture, token_fixture):
    mocker.patch(
        "icon_stats.crons.applications_refresh.get_local_application_tokens",
        return_value={"apps": [app_fixture], "tokens": [token_fixture]},
    )
    await cron()
