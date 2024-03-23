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

async def set_field_not_zero(
    application: Application,
    target_column: str,
    func: Callable[[str, str], Awaitable[int]],
    source_column: str = None,
):
    out = await func(source_column, application.id)
    setattr(application, target_column, out if out is not None else 0)


async def set_field(
    application: Application,
    column: str,
    func: Callable[[str, str], Awaitable[int]],
):
    for i in ["24h", "7d", "30d"]:
        column_name = f"{column}_{i}"
        prev_column_name = f"{column_name}_prev"
        await set_field_not_zero(application, column_name, func, column_name)
        await set_field_not_zero(application, prev_column_name, func, prev_column_name)


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
        await set_field_not_zero(
            i, "transaction_addresses_24h",
            get_contracts_sum, "unique_addresses_24h"
        )
        await set_field_not_zero(
            i, "transaction_addresses_7d",
            get_contracts_sum, "unique_addresses_7d"
        )
        await set_field_not_zero(
            i, "transaction_addresses_30d",
            get_contracts_sum, "unique_addresses_30d"
        )
        # Unique token transfer addresses
        await set_field_not_zero(
            i, "token_transfer_addresses_24h",
            get_tokens_sum, "unique_addresses_24h"
        )
        await set_field_not_zero(
            i, "token_transfer_addresses_7d",
            get_tokens_sum, "unique_addresses_7d"
        )
        await set_field_not_zero(
            i, "token_transfer_addresses_30d",
            get_tokens_sum, "unique_addresses_30d"
        )

        i.last_updated_timestamp = datetime.now(timezone.utc).timestamp()
        await i.upsert()

    prom_metrics.cron_ran.inc()
    logger.info(f"Ending {__name__} cron")
