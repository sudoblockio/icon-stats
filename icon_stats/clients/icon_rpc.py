from typing import ForwardRef, Generic, TypeVar

from pydantic import BaseModel, TypeAdapter

from icon_stats.clients.base import AsyncBaseClient, AsyncResponse
from icon_stats.clients.icon_rpc_iiss import GovernanceContractClient
from icon_stats.clients.icon_rpc_models.icx_call import GenericIcxCallModel
from icon_stats.clients.icon_rpc_models.icx_get_score_api import IcxGetScoreApiModel
from icon_stats.clients.icon_rpc_models.icx_get_transaction_result import (
    IcxGetTransactionResultModel,
)

ClientType = ForwardRef("AsyncIconRpcClient")


class IcxCallBuilder:
    def __init__(
        self,
        client: ClientType,
        to_address: str = None,
        contract_method: str = None,
        data_type: str = None,
        contract_params: dict = None,
        from_address: str = None,
        height: int = None,
        model_type: BaseModel = None,
        **kwargs,
    ):
        self.client = client
        self.to_address = to_address
        self.contract_method = contract_method
        self.data_type = data_type
        self.contract_params = contract_params
        self.from_address = from_address
        self.height = height
        self.model_type = model_type

        self.kwargs = kwargs

    def to_address(self, to_address: str) -> "IcxCallBuilder":
        self.to_address = to_address
        return self

    def contract_method(self, contract_method: str) -> "IcxCallBuilder":
        self.contract_method = contract_method
        return self

    def data_type(self, data_type: str) -> "IcxCallBuilder":
        self.data_type = data_type
        return self

    def contract_params(self, contract_params: dict) -> "IcxCallBuilder":
        self.contract_params = contract_params
        return self

    def from_address(self, from_address: str) -> "IcxCallBuilder":
        self.from_address = from_address
        return self

    def model_type(self, model_type: str) -> "IcxCallBuilder":
        self.model_type = model_type
        return self

    async def __call__(self, **kwargs):
        return await self.client.icx_call(
            to_address=self.to_address,
            method=self.contract_method,
            data_type=self.data_type,
            params=self.contract_params,
            from_address=self.from_address,
            height=self.height,
            **self.kwargs,
            **kwargs,
        )


class AsyncIconRpcClient(AsyncBaseClient):
    def __init__(
        self,
        base_url: str = "https://api.icon.community/api/v3",
        **kwargs,
    ):
        super().__init__(base_url, **kwargs)
        self.governance = GovernanceContractClient(self)

    def icx_call_builder(self, **kwargs) -> IcxCallBuilder:
        return IcxCallBuilder(self, **kwargs)

    async def icx_call(
        self,
        to_address: str,
        method: str,
        data_type: str = "call",
        params: dict = None,
        from_address: str = None,
        height: int = None,
        model_type: BaseModel = None,
        **kwargs,
    ) -> AsyncResponse:
        rpc_params = {
            "to": to_address,
            "dataType": data_type,
            "data": {"method": method},
        }
        if from_address is not None:
            rpc_params["from"] = from_address
        if params is not None:
            rpc_params["data"]["params"] = params
        if height is not None:
            rpc_params["height"] = hex(height)

        return AsyncResponse(
            response=await self.jsonrpc_request(
                rpc_method="icx_call",
                rpc_params=rpc_params,
                **kwargs,
            ),
            model_type=model_type if model_type is not None else GenericIcxCallModel,
        )

    async def icx_call_json(self, *args, **kwargs):
        r = await self.icx_call(*args, **kwargs)
        return await r.json()

    async def get_transaction_result(
        self,
        tx_hash: str,
        **kwargs,
    ) -> AsyncResponse[IcxGetTransactionResultModel]:
        return AsyncResponse(
            response=await self.jsonrpc_request(
                rpc_method="icx_getTransactionResult",
                rpc_params={"txHash": tx_hash},
                **kwargs,
            ),
            model_type=IcxGetTransactionResultModel,
        )

    async def get_score_api(
        self,
        address: str,
        **kwargs,
    ) -> AsyncResponse[IcxGetScoreApiModel]:
        return AsyncResponse(
            response=await self.jsonrpc_request(
                rpc_method="icx_getScoreApi",
                rpc_params={"address": address},
                **kwargs,
            ),
            model_type=IcxGetScoreApiModel,
        )
