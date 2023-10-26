from icon_stats.config import config
from icon_stats.clients.rest_client import RestClientFactory
from icon_stats.log import logger
from icon_stats.clients.rest_client import BaseRestClient


class CmcClient(BaseRestClient):
    def __init__(
            self,
            api_key: str,
            **kwargs,
    ):
        super().__init__(**kwargs)
        if api_key == "":
            logger.error("No CMC API Key. CMC APIs won't work...")
        self.headers = {
            'Accepts': 'application/json',
            'Accept-Encoding': 'deflate, gzip',
            'X-CMC_PRO_API_KEY': api_key
        }

    async def cryptocurrency_listings_latest(self, **params):
        output = await self.get(
            '/v1/cryptocurrency/listings/latest',
            params=params,
        )
        return output

    async def cryptocurrency_listings_historical(self, **params):
        output = await self.get(
            '/v1/cryptocurrency/listings/historical',
            params=params
        )
        return output

    async def cryptocurrency_quotes_latest(self, **params):
        output = await self.get(
            '/v1/cryptocurrency/quotes/latest',
            params=params
        )
        return output

    async def exchange_market_pairs_latest(self, **params):
        output = await self.get(
            '/v1/exchange/market-pairs/latest',
            params=params
        )
        return output


def new_cmc_client() -> CmcClient:
    return RestClientFactory.get_client(
        client_config=config.cmc,
        client=CmcClient,
    )
