from datetime import datetime, timezone

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
            last_updated = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
            # If your time is in a specific timezone, you can adjust it here.
            # Assuming UTC for this example.
            last_updated = last_updated.replace(tzinfo=timezone.utc)

    return last_updated.replace(tzinfo=None)
