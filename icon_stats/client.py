from icon_stats.clients.icon_rpc import AsyncIconRpcClient
from icon_stats.config import config


class ClientManager:
    _rpc_client: AsyncIconRpcClient = None

    @classmethod
    def get_rpc_client(cls) -> AsyncIconRpcClient:
        if cls._rpc_client is None:
            cls._rpc_client = AsyncIconRpcClient(base_url=config.ICON_NODE_URL)
        return cls._rpc_client


def get_rpc_client() -> AsyncIconRpcClient:
    return ClientManager.get_rpc_client()
