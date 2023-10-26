import aiohttp
from typing import Type, TypeVar
from threading import Lock

from icon_stats.clients.sessions import SessionManager
from icon_stats.config import config
from icon_stats.clients.configs import BaseRestClientConfig

class BaseRestClient:
    def __init__(
            self,
            endpoint: str,
            retries: int,
            timeout: int,
            session: aiohttp.ClientSession,
    ):
        self.session = session
        self.endpoint = endpoint
        self.retries = retries
        self.timeout = timeout
        self.headers = None

    async def _create_session(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()

    async def close(self):
        if self.session is not None and not self.session.closed:
            await self.session.close()

    async def get(self, path: str, **kwargs):
        url = f"{self.endpoint}{path}"
        async with self.session.get(url, headers=self.headers, **kwargs) as response:
            return await response.json()


# TypeVar to indicate any subclass of the BaseJsonRpcClient
TBaseRestClient = TypeVar('TBaseRestClient', bound=BaseRestClient)


class RestClientFactory:
    _clients = {}
    _lock = Lock()

    @classmethod
    def get_client(
            cls,
            client_config: Type[BaseRestClientConfig],
            client: Type[BaseRestClient],
    ) -> Type[TBaseRestClient]:
        """
        Gets a client by keeping a dict of all the chain clients and using the same
         aiohttp session for each in a threadsafe manner.
        """
        with cls._lock:
            client_class = client_config.__repr_name__()
            if client_class not in cls._clients:
                rpc_client_dict = {
                    'session': SessionManager.get_session(),
                    **config.cmc.__dict__,
                }
                cls._clients[client_class] = client(**rpc_client_dict)
            return cls._clients[client_class]
