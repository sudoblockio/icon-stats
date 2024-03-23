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

    for app in await Application.get_all():
        for contract_column in [
            "transactions",
            "fees_burned",
        ]:
            await set_field(app, contract_column, get_contracts_sum)
        for token_column in [
            "token_transfers",
            "volume",
        ]:
            await set_field(app, token_column, get_tokens_sum)
        # Unique transaction addresses
        for i in ["24h", "7d", "30d"]:
            await set_field_not_zero(
                app, f"transaction_addresses_{i}",
                get_contracts_sum, f"unique_addresses_{i}"
            )
            await set_field_not_zero(
                app, f"transaction_addresses_{i}_prev",
                get_contracts_sum, f"unique_addresses_{i}_prev"
            )
            await set_field_not_zero(
                app, f"token_transfer_addresses_{i}",
                get_tokens_sum, f"unique_addresses_{i}"
            )
            await set_field_not_zero(
                app, f"token_transfer_addresses_{i}_prev",
                get_tokens_sum, f"unique_addresses_{i}_prev"
            )

        app.last_updated_timestamp = datetime.now(timezone.utc).timestamp()
        await app.upsert()

    prom_metrics.cron_ran.inc()
    logger.info(f"Ending {__name__} cron")
