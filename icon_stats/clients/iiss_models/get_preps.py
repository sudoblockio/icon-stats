from pydantic import BaseModel, Field

from icon_stats.clients.types import HexBool, HexInt


class GetPRepsPRepModel(BaseModel):
    address: str
    bonded: HexInt
    city: str
    country: str
    delegated: HexInt
    details: str
    email: str
    grade: HexInt
    has_public_key: HexBool = Field(..., alias="hasPublicKey")
    irep: HexInt
    irep_update_block_height: str = Field(..., alias="irepUpdateBlockHeight")
    last_height: HexInt = Field(..., alias="lastHeight")
    name: str
    node_address: str = Field(..., alias="nodeAddress")
    p2p_endpoint: str = Field(..., alias="p2pEndpoint")
    penalty: str
    power: HexInt
    status: str
    total_blocks: HexInt = Field(..., alias="totalBlocks")
    validated_blocks: HexInt = Field(..., alias="validatedBlocks")
    website: str


class GetPRepsModel(BaseModel):
    block_height: HexInt = Field(..., alias="blockHeight")
    preps: list[GetPRepsPRepModel]
    start_ranking: HexInt = Field(..., alias="startRanking")
    total_delegated: HexInt = Field(..., alias="totalDelegated")
    total_stake: HexInt = Field(..., alias="totalStake")
