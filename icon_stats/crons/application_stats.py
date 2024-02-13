from datetime import datetime, timezone

from sqlalchemy.sql import text

from icon_stats.db import get_session
from icon_stats.log import logger
from icon_stats.metrics import prom_metrics
from icon_stats.models.applications import Application


async def get_contracts_sum(column, application_id) -> int:
    async with get_session(db_name="stats") as session:
        query = text(
            f"""
            select sum({column}) from stats.contracts
             where application_id = '{application_id}'
            """
        )
        result = await session.execute(query)
        return result.all()[0][0]


async def get_tokens_sum(column, application_id) -> int:
    async with get_session(db_name="stats") as session:
        query = text(
            f"""
            select sum({column})
            from stats.tokens as t inner join stats.contracts as c
            on t.address = c.address
            where c.application_id = '{application_id}'
            """
        )
        result = await session.execute(query)
        return result.all()[0][0]


async def run_application_stats():
    logger.info(f"Starting {__name__} cron")

    for i in await Application.get_all():
        i.transactions_24h = await get_contracts_sum("transactions_24h", i.id)
        i.transactions_7d = await get_contracts_sum("transactions_7d", i.id)
        i.transactions_30d = await get_contracts_sum("transactions_30d", i.id)
        #
        i.fees_burned_24h = await get_contracts_sum("fees_burned_24h", i.id)
        i.fees_burned_7d = await get_contracts_sum("fees_burned_7d", i.id)
        i.fees_burned_30d = await get_contracts_sum("fees_burned_30d", i.id)
        #
        i.token_transfers_24h = await get_tokens_sum("token_transfers_24h", i.id)
        i.token_transfers_7d = await get_tokens_sum("token_transfers_7d", i.id)
        i.token_transfers_30d = await get_tokens_sum("token_transfers_30d", i.id)
        #
        i.volume_24h = await get_tokens_sum("volume_24h", i.id)
        i.volume_7d = await get_tokens_sum("volume_7d", i.id)
        i.volume_30d = await get_tokens_sum("volume_30d", i.id)
        #
        i.last_updated_timestamp = datetime.now(timezone.utc).timestamp()
        await i.upsert()

    prom_metrics.cron_ran.inc()
    logger.info(f"Ending {__name__} cron")
