import pytest
from raiden_contracts.utils.config import C_TOKEN_NETWORK_REGISTRY
from .utils import *  # flake8: noqa


@pytest.fixture()
def get_token_network_registry(deploy_tester_contract):
    def get(arguments, transaction=None):
        return deploy_tester_contract(
            C_TOKEN_NETWORK_REGISTRY,
            {},
            arguments
        )
    return get


@pytest.fixture
def token_network_registry_contract(deploy_tester_contract, secret_registry_contract, web3):
    """Deployed TokenNetworksRegistry contract"""
    return deploy_tester_contract(
        'TokenNetworksRegistry',
        [],
        [secret_registry_contract.address, int(web3.version.network)]
    )


@pytest.fixture
def token_network_registry_address(token_network_registry_contract):
    """Address of TokenNetworksRegistry contract"""
    return token_network_registry_contract.address


@pytest.fixture
def add_and_register_token(
        web3,
        wait_for_transaction,
        token_network_registry_contract,
        deploy_token_contract,
        contract_deployer_address,
        contracts_manager
):
    """Deploy a token and register it in TokenNetworksRegistry"""
    def f(initial_amount: int, decimals: int, token_name: str, token_symbol: str):
        token_contract = deploy_token_contract(initial_amount, decimals, token_name, token_symbol)
        txid = token_network_registry_contract.functions.createERC20TokenNetwork(
            token_contract.address
        ).transact({'from': contract_deployer_address})
        tx_receipt = wait_for_transaction(txid)
        assert len(tx_receipt['logs']) == 1
        event_abi = contracts_manager.get_event_abi(
            'TokenNetworksRegistry',
            'TokenNetworkCreated'
        )
        decoded_event = get_event_data(event_abi, tx_receipt['logs'][0])
        assert decoded_event is not None
        assert is_address(decoded_event['args']['token_address'])
        assert is_address(decoded_event['args']['token_network_address'])
        token_network_address = decoded_event['args']['token_network_address']
        token_network_abi = contracts_manager.get_contract_abi('TokenNetwork')
        return web3.eth.contract(abi=token_network_abi, address=token_network_address)

    return f


