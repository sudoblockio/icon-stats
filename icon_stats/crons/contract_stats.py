from datetime import datetime, timezone

from sqlalchemy.sql import text

from icon_stats.db import get_session
from icon_stats.log import logger
from icon_stats.metrics import prom_metrics
from icon_stats.models.contracts import Contract
from icon_stats.utils.times import set_addr_func


async def get_transaction_count(address, start_time):
    async with get_session(db_name="transformer") as session:
        query = text(
            f"""
            select count(*) from transactions
             where (
                to_address = '{address}' or
                from_address = '{address}' or
                score_address = '{address}'
             ) and
             block_timestamp > {start_time}
            """
        )
        result = await session.execute(query)
        return result.scalar()


async def get_fees_sum(address, start_time):
    async with get_session(db_name="transformer") as session:
        query = text(
            f"""
            select transaction_fee from transactions
              where (
                to_address = '{address}' or
                from_address = '{address}' or
                score_address = '{address}'
              ) and
              block_timestamp > {start_time}
            """
        )
        result = await session.execute(query)
        hex_fees = result.all()
        return int(sum([int(i[0], 0) for i in hex_fees]) / 1e18)


async def get_unique_addresses(address, start_time):
    async with get_session(db_name="transformer") as session:
        query = text(
            f"""
            select count(distinct from_address) from transactions
             where score_address = '{address}' and
             block_timestamp > {start_time}
            """
        )
        result = await session.execute(query)
        return result.scalar()


async def run_contract_stats():
    logger.info(f"Starting {__name__} cron")

    for c in await Contract.get_all():
        for column, func, func_p in [
            ("transactions", get_transaction_count, get_transaction_count),
            ("fees_burned", get_fees_sum, get_fees_sum),
            ("unique_addresses", get_unique_addresses, get_unique_addresses),
        ]:
            await set_addr_func(c, column, func, func_p)

        c.last_updated_timestamp = datetime.now(timezone.utc).timestamp()
        await c.upsert()

    prom_metrics.cron_ran.inc()
    logger.info(f"Ending {__name__} cron")
