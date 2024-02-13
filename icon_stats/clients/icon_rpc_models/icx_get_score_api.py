from typing import Literal

from pydantic import BaseModel, Field, RootModel, TypeAdapter

from icon_stats.clients.types import HexBool

ScoreApiInputType = Literal[
    "int",
    "str",
    "bytes",
    "Address",
    "bool",
    "[]struct",
    "[]Address",
]


class IcxGetScoreApiItemInputModel(BaseModel):
    indexed: HexBool | None = None
    name: str
    type_: ScoreApiInputType = Field(alias="type")


ScoreApiType = Literal["function", "eventlog", "fallback"]


class IcxGetScoreApiItemModel(BaseModel):
    inputs: list[IcxGetScoreApiItemInputModel]
    name: str
    type_: ScoreApiType = Field(alias="type")
    readonly: HexBool | None = Field(None)


IcxGetScoreApiModel = TypeAdapter(list[IcxGetScoreApiItemModel])
