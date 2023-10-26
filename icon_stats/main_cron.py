from typing import Callable, TypedDict

from apscheduler.schedulers.background import BlockingScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from loguru import logger
from prometheus_client import start_http_server

from icon_stats.config import config
from icon_stats.db import session_factory
from icon_stats.crons import (
    top_tokens,
)


class Cron(TypedDict):
    func: Callable
    interval: int


CRONS: list[Cron] = [
    {
        "func": top_tokens.run_top_tokens,
        "interval": 600,
    },
]


def run_cron_with_session(cron: Callable):
    with session_factory() as session:
        cron(session=session)


def main():
    logger.info("Starting metrics server.")
    start_http_server(config.METRICS_PORT, config.METRICS_ADDRESS)

    # sched = BlockingScheduler()
    sched = AsyncIOScheduler()

    for i in CRONS:
        # Run the jobs immediately in order
        run_cron_with_session(i["func"])

        # Then run them in the scheduler
        sched.add_job(
            func=run_cron_with_session,
            trigger="interval",
            args=[i["func"]],
            seconds=i["interval"],
            id=i["func"].__name__,
        )

    sched.start()


if __name__ == "__main__":
    main()
