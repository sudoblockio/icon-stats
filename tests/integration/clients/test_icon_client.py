import pytest

from icon_stats.clients.icon_rpc import AsyncIconRpcClient, IcxCallBuilder


@pytest.mark.asyncio
async def test_icon_client_rpc_governance_get_iis_info():
    client = AsyncIconRpcClient()
    r = await client.governance.get_iis_info()
    model = await r.model()
    assert model


@pytest.mark.asyncio
async def test_icon_client_rpc_governance_get_preps():
    client = AsyncIconRpcClient()
    r = await client.governance.get_preps(end_ranking=10)
    output = await r.model()
    assert output.preps[0]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "tx_hash",
    [
        "0x8b77ce562c24776fcd4cc8f3e9427a3e1e0cc5bbef28eb6bc9c1211f46e87da8",
        "0x22efad3d3f53f0fdb8f13c897ab2b8a43ed9a3be436dfd2eee56fefe4b488e0a",
    ],
)
async def test_icon_client_rpc_get_transaction_result(tx_hash):
    client = AsyncIconRpcClient()
    r = await client.get_transaction_result(tx_hash=tx_hash)

    output = await r.model()
    assert output.event_logs


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "address",
    [
        "cx0000000000000000000000000000000000000000",  # gov
        # 'cx2e6d0fc0eca04965d06038c8406093337f085fcf',  # craft
        # 'cx21e94c08c03daee80c25d8ee3ea22a20786ec231',  # balanced router
        # 'cxa0af3165c08318e988cb30993b3048335b94af6c',  # balanced dex
    ],
)
async def test_icon_client_rpc_get_transaction_result(address):
    client = AsyncIconRpcClient()
    r = await client.get_score_api(address=address)

    json_output = await r.json()
    assert json_output
    model_output = await r.model()
    assert model_output[0].name


# @pytest.mark.asyncio
# async def test_client_call_builder():
#     client = AsyncIconRpcClient()
#
#     builder = client.icx_call_builder()
#     preps = builder.governance().make()
#
#
#     gov = client.governance()
#     preps = gov.get_preps()
#
#     builder2 = client.call_builder().to_address("hx000").data("foo")
#
#
# def test_builder():
#     client = AsyncIconRpcClient(base_url="https://api.icon.community/api/v3")
#     call = (
#         IcxCallBuilder(client)
#         .to_address("hx000")
#         .contract_method("foo")
#     )
#     pass
#
