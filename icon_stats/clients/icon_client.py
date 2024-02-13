from icon_stats.clients.base import AsyncBaseClient


class AsyncIconRestClient(AsyncBaseClient):
    def __init__(
        self,
        base_url: str = "https://tracker.icon.community/api/v1",
        **kwargs,
    ):
        super().__init__(base_url, **kwargs)
