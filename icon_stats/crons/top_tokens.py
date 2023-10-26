from icon_stats.log import logger
from sqlalchemy.orm import Session

from icon_stats.metrics import prom_metrics
from icon_stats.models.token_stats import TokenStats


def run_top_tokens(session: Session):
    """
    This cron ....
    """
    logger.info("Starting top tokens cron")

    top_tokens = session.execute("SELECT * FROM ")

    prom_metrics.cron_ran.inc()
    logger.info("Ending top tokens cron")


if __name__ == "__main__":
    from icon_stats.db import session_factory

    with session_factory() as session:
        run_top_tokens(session=session)
