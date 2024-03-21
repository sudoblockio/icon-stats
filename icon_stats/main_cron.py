import asyncio
from datetime import datetime, timezone
from typing import Any, Callable, Coroutine, TypedDict

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from loguru import logger
from prometheus_client import start_http_server
from sqlalchemy import text

from icon_stats.config import config
from icon_stats.crons import (
    application_stats,
    applications_refresh,
    cmc_cryptocurrency_quotes_latest,
    contract_stats,
    ecosystem_stats,
    token_stats,
)
from icon_stats.db import get_session

AsyncCallable = Callable[..., Coroutine[Any, Any, Any]]


class Cron(TypedDict):
    func: AsyncCallable
    interval: int
    table: str | None


CRONS: list[Cron] = [
    # {
    #     "func": cmc_cryptocurrency_quotes_latest.run_cmc_cryptocurrency_quotes_latest,
    #     "interval": 120,
    # }
    {
        "func": applications_refresh.run_applications_refresh,
        "interval": 86400,
        "table": None,
    },
    {
        "func": contract_stats.run_contract_stats,
        "interval": 3600 * 4,
        "table": "contracts",
    },
    {
        "func": token_stats.run_token_stats,
        "interval": 3600 * 4,
        "table": "tokens",
    },
    {
        "func": application_stats.run_application_stats,
        "interval": 3600 * 4,
        "table": "applications",
    },
    {
        "func": ecosystem_stats.run_ecosystem_stats,
        "interval": 3600 * 6,
        "table": "ecosystem",
    },
]


async def get_last_updated_timestamp(model: str):
    async with get_session("stats") as session:
        query = text(
            f"""
            SELECT last_updated_timestamp
             FROM stats.{model}
             ORDER BY last_updated_timestamp DESC  LIMIT 1;
            """
        )
        result = await session.execute(query)
        return result.first()


async def main():
    logger.info("Starting metrics server.")
    start_http_server(config.METRICS_PORT, config.METRICS_ADDRESS)

    sched = AsyncIOScheduler()

    # Refresh the list right away
    await applications_refresh.run_applications_refresh()

    for i in CRONS:
        # Run the jobs immediately in order
        if i["table"] is not None:
            last_updated_timestamp = await get_last_updated_timestamp(i["table"])
            current_timestamp = datetime.now(timezone.utc).timestamp()
            if last_updated_timestamp is None:
                await i["func"]()
            elif current_timestamp - last_updated_timestamp[0] > i["interval"]:
                await i["func"]()

        # Then run them in the scheduler
        sched.add_job(
            func=i["func"],
            trigger="interval",
            seconds=i["interval"],
            id=i["func"].__name__,
        )
    sched.start()
    try:
        while True:
            await asyncio.sleep(60)  # Sleep for a minute and check again.
    except (KeyboardInterrupt, SystemExit):
        pass


if __name__ == "__main__":
    asyncio.run(main())
