from datetime import datetime, timezone
from typing import Awaitable, Callable, Type

from icon_stats.db_base import BaseSQLModel


def convert_str_date(date_str: str) -> datetime:
    # Check if the date string ends with 'Z' (which means it's in UTC)
    if date_str.endswith("Z"):
        # If it does, we remove the 'Z' and parse the datetime as UTC.
        # The 'Z' is not supported by the fromisoformat method, so we have to handle it
        # manually.
        date_str = date_str.rstrip("Z")
        last_updated = datetime.fromisoformat(date_str)
        last_updated = last_updated.replace(tzinfo=timezone.utc)
    else:
        # If the string doesn't end with 'Z', we assume it's in local time (this may
        # not be a correct assumption depending on your data)
        # Here, you might want to handle other formats or timezones if necessary.
        try:
            last_updated = datetime.fromisoformat(date_str)
        except ValueError:
            # If parsing fails, we fall back to strptime with a defined format. Adjust
            # the format as necessary.
            last_updated = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            # If your time is in a specific timezone, you can adjust it here.
            # Assuming UTC for this example.
            last_updated = last_updated.replace(tzinfo=timezone.utc)

    return last_updated.replace(tzinfo=None)


def get_prev_star_time(start_time: int) -> int:
    current_timestamp = datetime.now(timezone.utc).timestamp()
    return int(start_time - (current_timestamp * 1e6 - start_time))


async def set_addr_func(
    model: Type[BaseSQLModel],
    column: str,
    func: Callable[[str, int], Awaitable[int]],
    func_p: Callable[[str, int], Awaitable[int]],
):
    """Used in both the contracts and tokens crons."""
    for days, str_name in [(1, "24h"), (7, "7d"), (30, "30d")]:
        current_timestamp = datetime.now(timezone.utc).timestamp()
        timestamp_ago = int((current_timestamp - 86400 * days) * 1e6)

        column_name = f"{column}_{str_name}"
        setattr(model, column_name, await func(model.address, timestamp_ago))
        # The previous columns
        prev_column_name = f"{column_name}_prev"
        setattr(model, prev_column_name, await func_p(model.address, timestamp_ago))
