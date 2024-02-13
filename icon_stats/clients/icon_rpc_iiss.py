from typing import TYPE_CHECKING, Type

from aiohttp import ClientResponse
from pydantic import BaseModel

from icon_stats.clients.base import AsyncResponse
from icon_stats.clients.iiss_models.get_iiss_info import GetIISSInfoModel
from icon_stats.clients.iiss_models.get_preps import GetPRepsModel

if TYPE_CHECKING:
    from icon_stats.clients.icon_rpc import AsyncIconRpcClient


class GovernanceContractClient:
    def __init__(self, client: "AsyncIconRpcClient"):
        self.client = client
        self.to_address = "cx0000000000000000000000000000000000000000"
        self.data_type = "call"

    async def _get(
        self,
        method: str,
        params: dict = None,
        model_type: Type[BaseModel] = None,
        **kwargs,
    ) -> AsyncResponse:
        return await self.client.icx_call(
            to_address=self.to_address,
            data_type=self.data_type,
            method=method,
            params=params,
            model_type=model_type,
            **kwargs,
        )

    async def get_preps(
        self,
        start_ranking: int = None,
        end_ranking: int = None,
        **kwargs,
    ) -> AsyncResponse:
        params = {}
        if start_ranking is not None:
            params["startRanking"] = hex(start_ranking)
        if end_ranking is not None:
            params["endRanking"] = hex(end_ranking)

        return await self._get(
            method="getPReps",
            params=params,
            model_type=GetPRepsModel,
            **kwargs,
        )

    async def get_iis_info(
        self,
        **kwargs,
    ) -> AsyncResponse[GetIISSInfoModel]:
        return await self._get(
            method="getIISSInfo",
            model_type=GetIISSInfoModel,
            **kwargs,
        )
