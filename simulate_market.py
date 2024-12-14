from ganache.ganache_manager import GanacheManager
from models.blockchain import Blockchain
from models.participant import Generator, Supplier
from matching.optimizer import TradeMatcher
import os
import json

def fund_accounts_with_spark(blockchain, accounts, amount):
    ganache_manager = GanacheManager()
    owner_account = ganache_manager.get_account(0)
    for account in accounts:
        tx = blockchain.token_contract.functions.transfer(
            account, amount
        ).build_transaction({
            'from': owner_account["address"],
            'nonce': blockchain.web3.eth.get_transaction_count(owner_account["address"]),
            'gas': 200000,
            'gasPrice': blockchain.web3.to_wei('20', 'gwei')
        })
        signed_tx = blockchain.web3.eth.account.sign_transaction(tx, private_key=owner_account["private_key"])
        tx_hash = blockchain.web3.eth.send_raw_transaction(signed_tx.raw_transaction)
        blockchain.web3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"Funded {account} with {amount} SPARK tokens.")


def run_simulation():
    token_abi_path = os.path.join("contracts", "SPARKToken.abi")
    trading_abi_path = os.path.join("contracts", "EnergyTrading.abi")

    provider_url = "http://127.0.0.1:8545"

    deployment_path = os.path.join("scripts", "deployment.json")
    with open(deployment_path, "r") as file:
        deployment_data = json.load(file)
    token_address = deployment_data["SPARKToken"]
    trading_address = deployment_data["EnergyTrading"]

    blockchain = Blockchain(provider_url, token_abi_path, token_address, trading_abi_path, trading_address)

    ganache_manager = GanacheManager()
    generator_address = ganache_manager.get_account(1)["address"]
    supplier_address = ganache_manager.get_account(2)["address"]

    fund_accounts_with_spark(blockchain, [generator_address, supplier_address], 5000)
    try:
        blockchain.add_liquidity(ganache_manager.get_account(0)["address"],
                                ganache_manager.get_account(0)["private_key"],
                                energy=2000, spark=10000)
    except Exception as e:
        print(f"Failed to add liquidity: {e}")

    total_energy = blockchain.trading_contract.functions.totalEnergyReserve().call()
    total_spark = blockchain.trading_contract.functions.totalSPARKReserve().call()
    print(f"Total Energy Reserve: {total_energy}")
    print(f"Total SPARK Reserve: {total_spark}")

    generators = [
        Generator(generator_id="Gen1", energy_capacity=500, price_per_unit=3, address=generator_address),
        Generator(generator_id="Gen2", energy_capacity=300, price_per_unit=5, address=generator_address),
        Generator(generator_id="Gen3", energy_capacity=200, price_per_unit=4, address=generator_address),
    ]
    suppliers = [
        Supplier(supplier_id="Sup1", energy_demand=400, max_price_per_unit=6, address=supplier_address),
        Supplier(supplier_id="Sup2", energy_demand=300, max_price_per_unit=7, address=supplier_address),
        Supplier(supplier_id="Sup3", energy_demand=200, max_price_per_unit=5, address=supplier_address),
    ]

    for gen in generators:
        gen.submit_offer(blockchain)

    for sup in suppliers:
        sup.submit_bid(blockchain)

    offers = blockchain.trading_contract.functions.getOffers().call()
    bids = blockchain.trading_contract.functions.getBids().call()

    optimizer = TradeMatcher(offers, bids)
    matched_trades = optimizer.optimize_matching()

    amm_price = blockchain.trading_contract.functions.getEnergyPrice().call()
    print(f"AMM Price: {amm_price} SPARK per unit of energy")

    for i, offer in enumerate(offers):
        print(f"Generator {i}: Price per Unit: {offer[2]}, AMM Price: {amm_price}")

    for j, bid in enumerate(bids):
        print(f"Supplier {j}: Max Price per Unit: {bid[2]}")

    for (offer_idx, bid_idx), trade_energy in matched_trades.items():
        try:
            # Fetch the offer and bid to log relevant details
            offer = offers[offer_idx]
            bid = bids[bid_idx]

            print(f"Executing Trade: Offer {offer_idx} -> Bid {bid_idx}")
            print(f"Offer Energy: {offer[1]}, Offer Price: {offer[2]}")
            print(f"Bid Energy: {bid[1]}, Bid Price: {bid[2]}")
            print(f"Requested Trade Energy: {trade_energy}")

            # Check the trade conditions before executing
            if trade_energy > offer[1]:
                print(f"Trade energy {trade_energy} exceeds offer energy {offer[1]}")
                continue
            if trade_energy > bid[1]:
                print(f"Trade energy {trade_energy} exceeds bid energy {bid[1]}")
                continue
            if bid[2] < offer[2]:
                print(f"Bid price {bid[2]} is lower than offer price {offer[2]}")
                continue

            # Execute the trade
            txn = blockchain.trading_contract.functions.executeTrade(
                offer_idx, bid_idx, int(trade_energy)
            ).build_transaction({
                'from': blockchain.web3.eth.accounts[0],
                'nonce': blockchain.web3.eth.get_transaction_count(blockchain.web3.eth.accounts[0]),
                'gas': 500000,  # Make sure we provide enough gas
                'gasPrice': blockchain.web3.to_wei('20', 'gwei')
            })

            # Print the transaction details before signing and sending
            print(f"Transaction: {txn}")

            # Sign the transaction using the private key of the account
            private_key = ganache_manager.get_account(0)["private_key"]  # Ensure you get the private key
            signed_tx = blockchain.web3.eth.account.sign_transaction(txn, private_key=private_key)
            tx_hash = blockchain.web3.eth.send_raw_transaction(signed_tx.raw_transaction)
            receipt = blockchain.web3.eth.wait_for_transaction_receipt(tx_hash)

            # Print the receipt to confirm the transaction
            print(f"Trade executed successfully: {receipt}")
            print(f"Transaction hash: {tx_hash.hex()}")

        except Exception as e:
            print(f"Trade failed: Offer {offer_idx} -> Bid {bid_idx}, Energy: {trade_energy}. Reason: {e}")

    print("Simulation completed. Check the blockchain for trade results.")


if __name__ == "__main__":
    run_simulation()
