import pytest

from icon_stats.clients.cmc import CmcClient, new_cmc_client


@pytest.fixture()
def cmc_client():
    return new_cmc_client()


@pytest.mark.asyncio
async def test_cmc_client_listings_current(cmc_client):
    output = await cmc_client.cryptocurrency_listings_latest()
    assert output


@pytest.mark.asyncio
async def test_cmc_client_listings_historical(cmc_client):
    # Not supported with basic subscription
    output = await cmc_client.cryptocurrency_listings_historical()
    assert output


@pytest.mark.asyncio
async def test_cmc_client_cryptocurrency_quotes_latest(cmc_client):
    output = await cmc_client.cryptocurrency_quotes_latest(symbol='ICX')
    assert output


@pytest.mark.asyncio
async def test_cmc_client_exchange_market_pairs_latest(cmc_client):
    # Not supported with basic subscription
    output = await cmc_client.exchange_market_pairs_latest(symbol='ICX')
    assert output
