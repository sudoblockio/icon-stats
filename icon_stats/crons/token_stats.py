from datetime import datetime, timezone

from sqlalchemy.sql import text

from icon_stats.db import get_session
from icon_stats.log import logger
from icon_stats.metrics import prom_metrics
from icon_stats.models.tokens import Token


async def get_token_transfer_count(address, start_time):
    async with get_session(db_name="transformer") as session:
        query = text(
            f"""
            select count(*) from token_transfers
             where token_contract_address = '{address}' and
             block_timestamp > {start_time}
            """
        )
        result = await session.execute(query)
        return result.scalar()


async def get_token_transfer_volume(address, start_time):
    async with get_session(db_name="transformer") as session:
        query = text(
            f"""
            select sum(value_decimal) from token_transfers
             where token_contract_address = '{address}' and
             block_timestamp > {start_time}
            """
        )
        result = await session.execute(query)
        return result.scalar()


async def get_fees_sum(address, start_time):
    async with get_session(db_name="transformer") as session:
        query = text(
            f"""
            select transaction_fee from token_transfers
             where token_contract_address = '{address}' and
             block_timestamp > {start_time}
            """
        )
        result = await session.execute(query)
        hex_fees = result.all()
        return int(sum([int(i[0], 0) for i in hex_fees]) / 1e18)


async def run_token_stats():
    """This refreshes the application list."""
    logger.info(f"Starting {__name__} cron")

    current_timestamp = datetime.now(timezone.utc).timestamp()
    times = {}
    for t in [1, 7, 30]:
        times[t] = int((current_timestamp - 86400 * t) * 1e6)

    tokens_db = await Token.get_all()

    for t in tokens_db:
        # Token transfers
        t.token_transfers_24h = await get_token_transfer_count(t.address, times[1])
        t.token_transfers_7d = await get_token_transfer_count(t.address, times[7])
        t.token_transfers_30d = await get_token_transfer_count(t.address, times[30])
        # Volume
        t.volume_24h = await get_token_transfer_volume(t.address, times[1])
        t.volume_7d = await get_token_transfer_volume(t.address, times[7])
        t.volume_30d = await get_token_transfer_volume(t.address, times[30])
        # Fees burned
        t.fees_burned_24h = await get_fees_sum(t.address, times[1])
        t.fees_burned_7d = await get_fees_sum(t.address, times[7])
        t.fees_burned_30d = await get_fees_sum(t.address, times[30])

        t.last_updated_timestamp = datetime.now(timezone.utc).timestamp()
        await t.upsert()

    prom_metrics.cron_ran.inc()
    logger.info(f"Ending {__name__} cron")
