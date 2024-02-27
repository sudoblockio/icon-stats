from datetime import datetime, timezone

from sqlalchemy.sql import text

from icon_stats.db import get_session
from icon_stats.log import logger
from icon_stats.metrics import prom_metrics
from icon_stats.models.tokens import Token
from icon_stats.utils.times import get_prev_star_time, set_addr_func


async def get_token_trans_count(address, start_time):
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


async def get_token_trans_count_p(address, start_time):
    async with get_session(db_name="transformer") as session:
        query = text(
            f"""
            select count(*) from token_transfers
             where token_contract_address = '{address}' and
             block_timestamp < {get_prev_star_time(start_time)}
             and block_timestamp > {start_time}
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


async def get_token_transfer_volume_p(address, start_time):
    async with get_session(db_name="transformer") as session:
        query = text(
            f"""
            select sum(value_decimal) from token_transfers
             where token_contract_address = '{address}' and
             block_timestamp < {start_time} and
             block_timestamp > {get_prev_star_time(start_time)}
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


async def get_fees_sum_p(address, start_time):
    async with get_session(db_name="transformer") as session:
        query = text(
            f"""
            select transaction_fee from token_transfers
             where token_contract_address = '{address}' and
             block_timestamp < {start_time} and
             block_timestamp > {get_prev_star_time(start_time)}
            """
        )
        result = await session.execute(query)
        hex_fees = result.all()
        return int(sum([int(i[0], 0) for i in hex_fees]) / 1e18)


async def get_unique_addrs(address, start_time):
    async with get_session(db_name="transformer") as session:
        query = text(
            f"""
            SELECT COUNT(DISTINCT address)
            FROM (
                SELECT from_address AS address
                FROM token_transfers
                WHERE token_contract_address = '{address}'
                  AND block_timestamp > {start_time}
                UNION
                SELECT to_address AS address
                FROM token_transfers
                WHERE token_contract_address = '{address}'
                  AND block_timestamp > {start_time}
            ) AS combined_addresses;
            """
        )
        result = await session.execute(query)
        return result.scalar()


async def get_unique_addrs_p(address, start_time):
    async with get_session(db_name="transformer") as session:
        query = text(
            f"""
            SELECT COUNT(DISTINCT address)
            FROM (
                SELECT from_address AS address
                FROM token_transfers
                WHERE token_contract_address = '{address}'
                  AND block_timestamp < {start_time}
                  AND block_timestamp > {get_prev_star_time(start_time)}
                UNION
                SELECT to_address AS address
                FROM token_transfers
                WHERE token_contract_address = '{address}'
                  AND block_timestamp < {start_time}
                  AND block_timestamp > {get_prev_star_time(start_time)}
            ) AS combined_addresses;
            """
        )
        result = await session.execute(query)
        return result.scalar()


async def run_token_stats():
    """This refreshes the application list."""
    logger.info(f"Starting {__name__} cron")

    for t in await Token.get_all():
        for column, func, func_p in [
            ("token_transfers", get_token_trans_count, get_token_trans_count_p),
            ("fees_burned", get_fees_sum, get_fees_sum_p),
            ("unique_addresses", get_unique_addrs, get_unique_addrs_p),
        ]:
            await set_addr_func(t, column, func, func_p)

        t.last_updated_timestamp = datetime.now(timezone.utc).timestamp()
        await t.upsert()

    prom_metrics.cron_ran.inc()
    logger.info(f"Ending {__name__} cron")
