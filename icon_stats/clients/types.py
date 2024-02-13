import re
from typing import Annotated

from pydantic import BeforeValidator, ValidationError


def _validate_re(regex: str, name: str):
    def f(v: str):
        if re.match(regex, v):
            return v
        raise ValidationError(f"Invalid {name}={v}")

    return f


HexInt = Annotated[int, BeforeValidator(lambda v: int(v, 0)), "Convert a hex str to int"]
HexBool = Annotated[bool, BeforeValidator(lambda v: bool(int(v, 0))), "Convert a hex str to bool"]


def _validate_address(v: str):
    if re.match(r"^(cx|hx)[0-9a-f]{40}$", v):
        return v
    raise ValidationError(f"Invalid address={v}")


Address = Annotated[
    str,
    BeforeValidator(_validate_re(r"^(cx|hx)[0-9a-f]{40}$", "address")),
    "A valid EOA or contract address",
]


def _validate_contract_address(v: str):
    if re.match(r"^cx[0-9a-f]{40}$", v):
        return v
    raise ValidationError(f"Invalid address={v}")


ContractAddress = Annotated[
    str, BeforeValidator(_validate_contract_address), "A valid EOA or contract address"
]


def _validate_tx_hash(v: str):
    if re.match(r"^0x[0-9a-f]{64}$", v):
        return v
    raise ValidationError(f"Invalid tx hash={v}")


TxHash = Annotated[
    str, BeforeValidator(_validate_re(r"^0x[0-9a-f]{64}$", "txHash")), "A transaction hash"
]
