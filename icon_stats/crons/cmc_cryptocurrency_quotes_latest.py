from icon_stats.log import logger
from sqlalchemy.orm import Session

from icon_stats.utils.times import convert_str_date
from icon_stats.metrics import prom_metrics
from icon_stats.models.cmc_cryptocurrency_quotes_latest import CmcListingsLatestQuote
from icon_stats.clients.cmc import new_cmc_client
from icon_stats.db_async import get_session, upsert_model


async def run_cmc_cryptocurrency_quotes_latest():
    """
    This cron scrapes the cmc endpoint for
    """
    logger.info("Starting top tokens cron")

    cmc_client = new_cmc_client()
    response = await cmc_client.cryptocurrency_quotes_latest(symbol='ICX')

    if isinstance(response, dict) and response['status']['error_code'] == 0:
        quote = response['data']['ICX']['quote']['USD']
    else:
        logger.info("Ending top tokens cron")
        return

    quote['last_updated'] = convert_str_date(quote['last_updated'])
    exchanges_legacy = CmcListingsLatestQuote(base='ICX', quote='USD', **quote)


    await upsert_model(db_name='stats', model=exchanges_legacy)

    prom_metrics.cron_ran.inc()
    logger.info("Ending top tokens cron")
