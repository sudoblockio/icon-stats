import pytest

from icon_stats.crons import (  # cmc_cryptocurrency_quotes_latest,
    application_stats,
    applications_refresh,
    contract_stats,
    ecosystem_stats,
    token_stats,
)

# @pytest.mark.asyncio
# async def test_crons_run_cmc_cryptocurrency_quotes_latest():
#     await cmc_cryptocurrency_quotes_latest.run_cmc_cryptocurrency_quotes_latest()


@pytest.fixture
def app_fixture():
    return


@pytest.fixture
def mock_application_refresh(mocker):
    mocker.patch(
        "icon_stats.crons.applications_refresh.get_remote_applications",
        return_value={
            "apps": [
                {
                    "id": "example",
                    "name": "",
                    "description": "",
                    "url": "",
                    "logo": "",
                    "contracts": [
                        "cx28b2ec885b50c8a93da752f2d0467a67127a70e8",
                    ],
                }
            ]
        },
    )

    class MockToken:
        address = "cx28b2ec885b50c8a93da752f2d0467a67127a70e8"
        _mapping = {"name": "crown", "address": address}

    mocker.patch(
        "icon_stats.crons.applications_refresh.get_all_tokens",
        return_value=[MockToken],
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "cron",
    [
        # applications_refresh.run_applications_refresh,
        # contract_stats.run_contract_stats,
        # token_stats.run_token_stats,
        # application_stats.run_application_stats,
        # ecosystem_stats.run_ecosystem_stats,
    ],
)
async def test_crons(cron, app_fixture, mock_application_refresh):
    await cron()
