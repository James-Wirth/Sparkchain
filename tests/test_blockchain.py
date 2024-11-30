import pytest
from models.blockchain import Blockchain
from ganache.ganache_manager import GanacheManager
import os
import json

@pytest.fixture
def blockchain():
    provider_url = "http://127.0.0.1:8545"

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    token_abi_path = os.path.join(base_dir, "contracts", "SPARKToken.abi")
    trading_abi_path = os.path.join(base_dir, "contracts", "EnergyTrading.abi")

    deployment_path = os.path.join(os.path.dirname(__file__), "../scripts/deployment.json")
    with open(deployment_path, "r") as file:
        deployment_data = json.load(file)
    token_address = deployment_data["SPARKToken"]
    trading_address = deployment_data["EnergyTrading"]

    return Blockchain(provider_url, token_abi_path, token_address, trading_abi_path, trading_address)

def test_add_liquidity(blockchain):
    ganache_manager = GanacheManager()
    account = ganache_manager.get_account(0)["address"]
    private_key =ganache_manager.get_account(0)["private_key"]
    tx = blockchain.add_liquidity(account, private_key, energy=1000, spark=5000)
    assert tx is not None


def test_submit_offer(blockchain):
    ganache_manager = GanacheManager()
    account = ganache_manager.get_account(0)["address"]
    tx = blockchain.trading_contract.functions.submitOffer(100, 10).transact({'from': account})
    assert tx is not None


def test_submit_bid(blockchain):
    ganache_manager = GanacheManager()
    account = ganache_manager.get_account(0)["address"]
    tx = blockchain.trading_contract.functions.submitBid(100, 15).transact({'from': account})
    assert tx is not None
