from datetime import datetime, timezone
from typing import Awaitable, Callable

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
            select sum(t.{column})
            from stats.tokens as t inner join stats.contracts as c
            on t.address = c.address
            where c.application_id = '{application_id}'
            """
        )
        result = await session.execute(query)
        return result.all()[0][0]


async def set_field(
    application: Application,
    column: str,
    func: Callable[[str, str], Awaitable[int]],
    target_column: str = None,
):
    for i in ["24h", "7d", "30d"]:
        column_name = f"{column}_{i}"
        if target_column is None:
            target_column = column_name
        prev_column_name = f"{column_name}_prev"
        setattr(application, column_name, await func(target_column, application.id))
        setattr(application, prev_column_name, await func(target_column, application.id))


async def run_application_stats():
    logger.info(f"Starting {__name__} cron")

    for i in await Application.get_all():
        for contract_column in [
            "transactions",
            "fees_burned",
        ]:
            await set_field(i, contract_column, get_contracts_sum)
        for token_column in [
            "token_transfers",
            "volume",
        ]:
            await set_field(i, token_column, get_tokens_sum)
        # Unique transaction addresses
        i.transaction_addresses_24h = await get_contracts_sum("unique_addresses_24h", i.id)
        i.transaction_addresses_7d = await get_contracts_sum("unique_addresses_7d", i.id)
        i.transaction_addresses_30d = await get_contracts_sum("unique_addresses_30d", i.id)
        # Unique token transfer addresses
        i.token_transfer_addresses_24h = await get_tokens_sum("unique_addresses_24h", i.id)
        i.token_transfer_addresses_7d = await get_tokens_sum("unique_addresses_7d", i.id)
        i.token_transfer_addresses_30d = await get_tokens_sum("unique_addresses_30d", i.id)

        i.last_updated_timestamp = datetime.now(timezone.utc).timestamp()
        await i.upsert()

    prom_metrics.cron_ran.inc()
    logger.info(f"Ending {__name__} cron")
