import aiohttp


class SessionManager:
    """Ensure a single aiohttp session shared between all the clients."""
    _session = None

    @classmethod
    def get_session(cls) -> aiohttp.ClientSession:
        if cls._session is None:
            cls._session = aiohttp.ClientSession()
        return cls._session
