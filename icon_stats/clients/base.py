import asyncio
import itertools
import json
from typing import Any, Generic, Type, TypeVar

from aiohttp import ClientResponse, ClientSession, TCPConnector
from pydantic import BaseModel, TypeAdapter


class BaseResponseException(Exception):
    pass


class HttpException(BaseResponseException):
    pass


class JsonRpcException(BaseResponseException):
    pass


# ModelType = TypeVar("ModelType", bound=BaseModel | RootModel)
ModelType = TypeVar("ModelType", bound=BaseModel | TypeAdapter)


class AsyncResponse(Generic[ModelType]):
    def __init__(
        self,
        response: ClientResponse,
        model_type: Type[ModelType] = None,
    ):
        self.response_raw = response
        self.model_type = model_type
        self._json = None
        self._json_is_obj = None

        # TODO: Move to middleware
        if not self.response_raw.ok:
            raise HttpException()

    @property
    def status_code(self) -> int:
        return self.response_raw.status

    @property
    def status_ok(self) -> int:
        return self.response_raw.status == 200

    async def json(self) -> dict:
        if self._json is None:
            self._json = await self.response_raw.json()
        # TODO: json rpc error middleware
        if "error" in self._json:
            raise JsonRpcException(self._json["error"])
        return self._json["result"]

    async def model(self) -> ModelType:
        # TODO: Thiw will be part of code gen most likely...
        # We should probably just base this off the type in the json response?
        if isinstance(self.model_type, TypeAdapter):
            return self.model_type.validate_python(await self.json())
        if isinstance(self.model_type, BaseModel):
            # For some reason it is not catching this... It should
            return self.model_type.model_validate(**await self.json())
        return self.model_type(**await self.json())  # Above should have been caught


class AsyncBaseClient:
    def __init__(
        self,
        base_url: str,
        *,
        path_url: str = None,
        auth: tuple = None,
        limit: int = None,
        headers: dict = None,
        connector: TCPConnector = None,
        connector_kwargs: dict = None,
        session: ClientSession = None,
        session_kwargs: dict = None,
    ):
        self.request_counter = itertools.count()
        self.base_url = base_url
        self.path_url = path_url

        self.auth = auth
        self.limit = limit
        self.headers = headers

        self.asyncio_loop = asyncio.get_event_loop()
        self.connector = self.get_connector(connector, connector_kwargs)

        if session is None:
            if session_kwargs is None:
                session_kwargs = {}
            self.session = self.get_session(**session_kwargs)
        else:
            self.session = session

    def get_connector(
        self,
        connector: TCPConnector | None,
        connector_kwargs: dict | None,
    ) -> TCPConnector:
        if connector is None:
            if connector_kwargs is None:
                connector_kwargs = {}
            return TCPConnector(**connector_kwargs, loop=self.asyncio_loop)
        else:
            return connector

    def get_session(self, **kwargs) -> ClientSession:
        return ClientSession(
            loop=self.asyncio_loop,
            connector=self.connector,
            **kwargs,
        )

    async def jsonrpc_request(
        self,
        rpc_method: str,
        rpc_params: Any,
        **kwargs,
    ) -> ClientResponse:
        return await self.session.post(
            self.base_url,
            data=json.dumps(
                {
                    "jsonrpc": "2.0",
                    "method": rpc_method,
                    "params": rpc_params,
                    "id": next(self.request_counter),
                }
            ),
            headers={"Content-Type": "application/json"},  # Request level header
            **kwargs,
        )

    async def __aenter__(self):
        self.session = await self.session.__aenter__()
        return self  #

    async def __aexit__(self, exc_type, exc_val, traceback):
        await self.session.__aexit__(exc_type, exc_val, traceback)
