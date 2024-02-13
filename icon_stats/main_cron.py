import asyncio
from typing import Any, Callable, Coroutine, TypedDict

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from loguru import logger
from prometheus_client import start_http_server

from icon_stats.config import config
from icon_stats.crons import (
    application_stats,
    applications_refresh,
    cmc_cryptocurrency_quotes_latest,
    contract_stats,
    token_stats,
)

AsyncCallable = Callable[..., Coroutine[Any, Any, Any]]


class Cron(TypedDict):
    func: AsyncCallable
    interval: int


CRONS: list[Cron] = [
    # {
    #     "func": cmc_cryptocurrency_quotes_latest.run_cmc_cryptocurrency_quotes_latest,
    #     "interval": 120,
    # }
    {
        "func": applications_refresh.run_applications_refresh,
        "interval": 86400,
    },
    {
        "func": contract_stats.run_contract_stats,
        "interval": 3600 * 4,
    },
    {
        "func": token_stats.run_token_stats,
        "interval": 3600 * 4,
    },
    {
        "func": application_stats.run_application_stats,
        "interval": 3600 * 4,
    },
]


async def main():
    logger.info("Starting metrics server.")
    start_http_server(config.METRICS_PORT, config.METRICS_ADDRESS)

    sched = AsyncIOScheduler()

    for i in CRONS:
        # Run the jobs immediately in order
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
