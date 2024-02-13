import json
import os

import requests

from icon_stats.client import get_rpc_client
from icon_stats.clients.base import BaseResponseException
from icon_stats.log import logger
from icon_stats.metrics import prom_metrics
from icon_stats.models.applications import Application
from icon_stats.models.contracts import Contract
from icon_stats.models.tokens import Token


def get_remote_application_tokens() -> (dict, dict):
    base_url = "https://raw.githubusercontent.com/PARROT9-LTD"
    r = requests.get(f"{base_url}/icondashboard-list-apps/main/apps/index.json")
    if r.status_code != 200:
        raise Exception(f"Error getting application list: {r.status_code}")
    output = r.json()

    return output


def get_local_application_tokens() -> (dict, dict):
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
        token.symbol = await client.icx_call_json(to_address=token.address, method="symbol")
        token.decimals = int(
            await client.icx_call_json(to_address=token.address, method="decimals"), 0
        )
    except BaseResponseException as e:
        print(f"{e}\n\nGet name: {token.address}")


async def run_applications_refresh():
    """This refreshes the application list."""
    logger.info(f"Starting {__name__} cron")

    # applications_raw, tokens_raw = get_remote_application_tokens()
    output = get_local_application_tokens()

    applications_raw = output["apps"]
    tokens_raw = output["tokens"]

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
    try:
        for i in tokens_raw:
            token_db = await Token.get(Token.address == i["contract"])
            if token_db is None:
                address = i.pop("contract")
                token_db = Token(**i, address=address)
            await update_token_details(token_db)
            await token_db.upsert()
    except Exception as e:
        raise e

    prom_metrics.cron_ran.inc()
    logger.info(f"Ending {__name__} cron")
