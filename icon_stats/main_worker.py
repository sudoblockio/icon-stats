from loguru import logger
from prometheus_client import start_http_server

from icon_stats.config import config
from icon_stats.workers.transactions import (
    transactions_worker_head,
    transactions_worker_tail,
)


def main(worker_type: str = "head"):
    logger.info("Starting metrics server.")
    start_http_server(config.METRICS_PORT, config.METRICS_ADDRESS)

    logger.info(f"Worker is a {worker_type}.")

    if worker_type == "head":
        transactions_worker_head()
    if worker_type == "tail":
        transactions_worker_tail()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Worker type input.")
    parser.add_argument("worker_type", type=str, help="The type of worker", default="")
    args = parser.parse_args()
    main(args.worker_type)
    # main()
