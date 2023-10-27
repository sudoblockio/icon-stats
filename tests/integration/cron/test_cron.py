import pytest

from icon_stats.crons import (
    cmc_cryptocurrency_quotes_latest
)


# @pytest.mark.order(1)
@pytest.mark.asyncio
async def test_crons_run_cmc_cryptocurrency_quotes_latest():
    await cmc_cryptocurrency_quotes_latest.run_cmc_cryptocurrency_quotes_latest()
