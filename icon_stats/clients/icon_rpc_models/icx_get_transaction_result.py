from pydantic import BaseModel, Field

from icon_stats.clients.types import HexBool, HexInt


class IcxGetTransactionResultEventLogsModel(BaseModel):
    score_address: str = Field(..., alias="scoreAddress")
    indexed: list[str]
    data: list[str]


class IcxGetTransactionResultModel(BaseModel):
    block_hash: HexInt = Field(alias="blockHash")
    block_height: HexInt = Field(alias="blockHeight")
    cumulative_step_used: HexInt = Field(alias="cumulativeStepUsed")
    event_logs: list[IcxGetTransactionResultEventLogsModel] = Field(alias="eventLogs")
    logs_bloom: HexInt = Field(alias="logsBloom")
    status: HexInt
    step_price: HexInt = Field(alias="stepPrice")
    step_used: HexInt = Field(alias="stepUsed")
    to: str
    tx_hash: str = Field(alias="txHash")
    tx_index: HexInt = Field(alias="txIndex")
