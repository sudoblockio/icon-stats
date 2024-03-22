import json
import os

import requests
from sqlalchemy import text

from icon_stats.client import get_rpc_client
from icon_stats.clients.base import BaseResponseException
from icon_stats.db import get_session
from icon_stats.log import logger
from icon_stats.metrics import prom_metrics
from icon_stats.models.applications import Application
from icon_stats.models.contracts import Contract
from icon_stats.models.tokens import Token


def get_local_applications() -> (dict, dict):
    data_path = os.path.join(os.path.dirname(__file__), "..", "..", "data")
    with open(f"{data_path}/applications.json") as f:
        output = json.load(f)

    return output


async def update_contract_details(contract: Contract):
    try:
        client = get_rpc_client()
        r_name = await client.icx_call(to_address=contract.address, method="name")
        contract.name = await r_name.json()
    except BaseResponseException as e:
        print(f"{e}\n\nGet name: {contract.address}")


async def update_token_details(token: Token):
    try:
        client = get_rpc_client()

        token.name = await client.icx_call_json(to_address=token.address, method="name")
        token.symbol = await client.icx_call_json(
            to_address=token.address,
            method="symbol",
        )
        token.decimals = int(
            await client.icx_call_json(to_address=token.address, method="decimals"), 0
        )
    except BaseResponseException as e:
        print(f"{e}\n\nGet name: {token.address}")


async def create_other_application():
    if await Application.get(Application.name == "other") is None:
        await Application(
            id="other",
            name="other",
            description="Any non-classified contract. Add to the list if you want it " "tracked.",
        ).upsert()


async def create_applications():
    output = get_local_applications()

    applications_raw = output["apps"]
    await create_other_application()

    for i in applications_raw:
        try:
            application_db = await Application.get(Application.name == i["name"])
            contracts_list = i.pop("contracts")
            if application_db is None:
                application_db = Application(**i)
            await application_db.upsert()

            for address in contracts_list:
                contract_db = await Contract.get(Contract.address == address)
                if contract_db is None:
                    contract_db = Contract(
                        address=address,
                        application_id=i["id"],
                    )
                await update_contract_details(contract_db)
                await contract_db.upsert()

        except Exception as e:
            raise e


async def get_all_tokens():
    async with get_session(db_name="contracts") as session:
        query = text(
            f"""
            select address, name, symbol, decimals, contract_type, is_nft
             from contracts
             where is_token = true and is_nft = false
            """
        )
        result = await session.execute(query)
        return result.fetchall()


async def create_other_contract(address: str):
    if await Contract.get(Contract.address == address) is None:
        contract = Contract(
            address=address,
            application_id="other",
        )
        await update_contract_details(contract)
        await contract.upsert()


async def create_tokens():
    try:
        for token_contracts_db in await get_all_tokens():
            address = token_contracts_db.address
            token_db = await Token.get(Token.address == address)
            if token_db is None:
                await create_other_contract(address)
                token_db = Token(**token_contracts_db._mapping, application_id="other")
            await token_db.upsert()
    except Exception as e:
        raise e


async def run_applications_refresh():
    """This refreshes the application list."""
    logger.info(f"Starting {__name__} cron")

    await create_applications()
    await create_tokens()

    prom_metrics.cron_ran.inc()
    logger.info(f"Ending {__name__} cron")
