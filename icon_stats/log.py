import json
from loguru import logger

from icon_stats.config import config


def sink(message):
    record = message.record
    log_data = {
        "timestamp": record["time"].strftime('%Y-%m-%d %H:%M:%S'),
    }

    if "structured" in record["extra"]:
        log_data["data"] = record["extra"]["structured"]
    else:
        log_data["message"] = record["message"]

    if config.LOG_FORMAT == "json":
        return json.dumps(log_data, indent=config.STRUCTURED_SETTINGS.INDENT)
    else:
        return log_data["message"]


logger.remove()
logger.add(sink, level=config.LOG_LEVEL, enqueue=True)

# If logging to a file
if config.LOG_TO_FILE:
    logger.add(config.LOG_FILE_NAME, level=config.LOG_LEVEL, enqueue=True)
