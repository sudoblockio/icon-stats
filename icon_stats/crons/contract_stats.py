from datetime import datetime, timezone

from sqlalchemy.sql import text

from icon_stats.db import get_session
from icon_stats.log import logger
from icon_stats.metrics import prom_metrics
from icon_stats.models.contracts import Contract


async def get_transaction_count(address, start_time):
    async with get_session(db_name="transformer") as session:
        query = text(
            f"""
            select count(*) from transactions
             where (
                to_address = '{address}' or
                from_address = '{address}'
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
             where (to_address = '{address}' or
             from_address = '{address}') and
             block_timestamp > {start_time}
            """
        )
        result = await session.execute(query)
        hex_fees = result.all()
        return int(sum([int(i[0], 0) for i in hex_fees]) / 1e18)


async def execute(query):
    async with get_session(db_name="stats") as session:
        return await session.execute(query)


async def run_contract_stats():
    logger.info(f"Starting {__name__} cron")

    current_timestamp = datetime.now(timezone.utc).timestamp()
    timestamps = {}
    for t in [1, 7, 30]:
        timestamps[t] = int((current_timestamp - 86400 * t) * 1e6)

    # contracts =
    for c in await Contract.get_all():
        # Transactions
        c.transactions_24h = await get_transaction_count(c.address, timestamps[1])
        c.transactions_7d = await get_transaction_count(c.address, timestamps[7])
        c.transactions_30d = await get_transaction_count(c.address, timestamps[30])
        # Fees
        c.fees_burned_24h = await get_fees_sum(c.address, timestamps[1])
        c.fees_burned_7d = await get_fees_sum(c.address, timestamps[7])
        c.fees_burned_30d = await get_fees_sum(c.address, timestamps[30])
        #
        c.last_updated_timestamp = datetime.now(timezone.utc).timestamp()
        await c.upsert()

    prom_metrics.cron_ran.inc()
    logger.info(f"Ending {__name__} cron")
