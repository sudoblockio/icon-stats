from pydantic import BaseModel, Field, computed_field

from icon_stats.clients.types import HexInt


class GetIISSInfoRcResultModel(BaseModel):
    end_block_height: HexInt = Field(..., alias="endBlockHeight")
    estimated_icx: HexInt = Field(..., alias="estimatedICX")
    iscore: HexInt
    start_block_height: HexInt = Field(..., alias="startBlockHeight")
    state_hash: HexInt = Field(..., alias="stateHash")


class GetIISSInfoValueModel(BaseModel):
    icps: HexInt = Field(..., alias="Icps")
    iglobal: HexInt = Field(..., alias="Iglobal")
    iprep: HexInt = Field(..., alias="Iprep")
    irelay: HexInt = Field(..., alias="Irelay")
    ivoter: HexInt = Field(..., alias="Ivoter")


class GetIISSInfoModel(BaseModel):
    block_height: HexInt = Field(..., alias="blockHeight")
    next_calculation: HexInt = Field(..., alias="nextCalculation")
    next_prep_term: HexInt = Field(..., alias="nextPRepTerm")
    rc_result: GetIISSInfoRcResultModel = Field(..., alias="rcResult")
    variable: GetIISSInfoValueModel

    @property
    @computed_field
    def decode(self):
        # TODO
        return
