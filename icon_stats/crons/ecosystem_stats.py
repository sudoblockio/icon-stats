from datetime import datetime, timezone
from typing import Awaitable, Callable

from sqlalchemy.sql import text

from icon_stats.db import get_session
from icon_stats.log import logger
from icon_stats.metrics import prom_metrics
from icon_stats.models.ecosystem import Ecosystem
from icon_stats.utils.times import get_prev_star_time


async def get_transaction_count(start_time):
    async with get_session(db_name="transformer") as session:
        query = text(
            f"""
            select count(*) from transactions
             where block_timestamp > {start_time} and
             score_address != 'hx1000000000000000000000000000000000000000'
            """
        )
        result = await session.execute(query)
        return result.scalar()


async def get_transaction_count_p(start_time):
    async with get_session(db_name="transformer") as session:
        query = text(
            f"""
            select count(*) from transactions
             where block_timestamp < {start_time} and
             block_timestamp > {get_prev_star_time(start_time)} and
             score_address != 'hx1000000000000000000000000000000000000000'
            """
        )
        result = await session.execute(query)
        return result.scalar()


async def get_fees_sum(start_time):
    async with get_session(db_name="transformer") as session:
        query = text(
            f"""
            select transaction_fee from transactions
             where block_timestamp > {start_time} and
             score_address != 'hx1000000000000000000000000000000000000000'
            """
        )
        result = await session.execute(query)
        hex_fees = result.all()
        return int(sum([int(i[0], 0) for i in hex_fees]) / 1e18)


async def get_fees_sum_p(start_time):
    async with get_session(db_name="transformer") as session:
        query = text(
            f"""
            select transaction_fee from transactions
             where block_timestamp < {get_prev_star_time(start_time)}
             and block_timestamp > {start_time} and
             score_address != 'hx1000000000000000000000000000000000000000'
            """
        )
        result = await session.execute(query)
        hex_fees = result.all()
        return int(sum([int(i[0], 0) for i in hex_fees]) / 1e18)


async def get_unique_addresses(start_time):
    async with get_session(db_name="transformer") as session:
        query = text(
            f"""
            select count(distinct from_address) from transactions
             where block_timestamp > {start_time}
            """
        )
        result = await session.execute(query)
        return result.scalar()


async def get_unique_addresses_p(start_time):
    async with get_session(db_name="transformer") as session:
        query = text(
            f"""
            select count(distinct from_address) from transactions            
             where block_timestamp < {get_prev_star_time(start_time)}
             and block_timestamp > {start_time}
            """
        )
        result = await session.execute(query)
        return result.scalar()


async def get_token_trans_count(start_time):
    async with get_session(db_name="transformer") as session:
        query = text(
            f"""
            select count(*) from token_transfers
             where block_timestamp > {start_time}
            """
        )
        result = await session.execute(query)
        return result.scalar()


async def get_token_trans_count_p(start_time):
    async with get_session(db_name="transformer") as session:
        query = text(
            f"""
            select count(*) from token_transfers
             where block_timestamp < {get_prev_star_time(start_time)}
             and block_timestamp > {start_time}
            """
        )
        result = await session.execute(query)
        return result.scalar()


async def get_unique_token_addrs(start_time):
    async with get_session(db_name="transformer") as session:
        query = text(
            f"""
            SELECT COUNT(DISTINCT address)
            FROM (
                SELECT from_address AS address
                FROM token_transfers
                WHERE block_timestamp > {start_time}
                UNION
                SELECT to_address AS address
                FROM token_transfers
                WHERE block_timestamp > {start_time}
            ) AS combined_addresses;
            """
        )
        result = await session.execute(query)
        return result.scalar()


async def get_unique_token_addrs_p(start_time):
    async with get_session(db_name="transformer") as session:
        query = text(
            f"""
            SELECT COUNT(DISTINCT address)
            FROM (
                SELECT from_address AS address
                FROM token_transfers
                WHERE block_timestamp < {start_time}
                  AND block_timestamp > {get_prev_star_time(start_time)}
                UNION
                SELECT to_address AS address
                FROM token_transfers
                WHERE block_timestamp < {start_time}
                  AND block_timestamp > {get_prev_star_time(start_time)}
            ) AS combined_addresses;
            """
        )
        result = await session.execute(query)
        return result.scalar()


async def set_attr_func(
    model: Ecosystem,
    column: str,
    func: Callable[[int], Awaitable[int]],
    func_p: Callable[[int], Awaitable[int]],
):
    """Used in both the contracts and tokens crons."""
    for days, str_name in [(1, "24h"), (7, "7d"), (30, "30d")]:
        current_timestamp = datetime.now(timezone.utc).timestamp()
        timestamp_ago = int((current_timestamp - 86400 * days) * 1e6)

        column_name = f"{column}_{str_name}"
        out = await func(timestamp_ago)
        setattr(model, column_name, out if out is not None else 0)
        # The previous columns
        out = await func_p(timestamp_ago)
        setattr(model, f"{column_name}_prev", out if out is not None else 0)


async def run_ecosystem_stats():
    logger.info(f"Starting {__name__} cron")

    model = await Ecosystem.get(Ecosystem.id == 0)
    if model is None:
        model = Ecosystem(id=0)

    for column, func, func_p in [
        ("transactions", get_transaction_count, get_transaction_count_p),
        ("fees_burned", get_fees_sum, get_fees_sum_p),
        ("unique_addresses", get_unique_addresses, get_unique_addresses_p),
        ("token_transfers", get_token_trans_count, get_token_trans_count_p),
        ("token_transfer_addresses", get_unique_token_addrs, get_unique_token_addrs_p),
    ]:
        await set_attr_func(model, column, func, func_p)
        await model.upsert()

    model.last_updated_timestamp = datetime.now(timezone.utc).timestamp()
    await model.upsert()

    prom_metrics.cron_ran.inc()
    logger.info(f"Ending {__name__} cron")
