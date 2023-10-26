from fastapi import Depends

from icon_stats.db import get_session


def is_database_online(session: bool = Depends(get_session)):
    return session
