import asyncio
from typing import Callable, TypedDict, Coroutine, Any
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from loguru import logger
from prometheus_client import start_http_server

from icon_stats.config import config
from icon_stats.crons import (
    top_tokens,
    cmc_cryptocurrency_quotes_latest,
)

AsyncCallable = Callable[..., Coroutine[Any, Any, Any]]


class Cron(TypedDict):
    func: AsyncCallable
    interval: int


CRONS: list[Cron] = [
    # {
    #     "func": top_tokens.run_top_tokens,
    #     "interval": 600,
    # },
    {
        "func": cmc_cryptocurrency_quotes_latest.run_cmc_cryptocurrency_quotes_latest,
        "interval": 120,
    }

]


async def main():
    logger.info("Starting metrics server.")
    start_http_server(config.METRICS_PORT, config.METRICS_ADDRESS)

    # sched = BlockingScheduler()
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
        pass
    sched.start()
    try:
        while True:
            await asyncio.sleep(60)  # Sleep for a minute and check again.
    except (KeyboardInterrupt, SystemExit):
        pass


if __name__ == "__main__":
    asyncio.run(main())
