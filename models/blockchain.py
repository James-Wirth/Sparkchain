from web3 import Web3
import json


class Blockchain:
    def __init__(self, provider_url, token_abi_path, token_address, trading_abi_path, trading_address):
        self.web3 = Web3(Web3.HTTPProvider(provider_url))
        self.token_address = Web3.to_checksum_address(token_address)
        self.trading_address = Web3.to_checksum_address(trading_address)

        with open(token_abi_path, 'r') as file:
            self.token_abi = json.load(file)
        with open(trading_abi_path, 'r') as file:
            self.trading_abi = json.load(file)

        self.token_contract = self.web3.eth.contract(address=self.token_address, abi=self.token_abi)
        self.trading_contract = self.web3.eth.contract(address=self.trading_address, abi=self.trading_abi)

    def validate_private_key(self, private_key):
        if len(private_key) != 66:
            raise ValueError(f"Invalid private key length: {len(private_key)}. It should be 66 characters.")

    def add_liquidity(self, account, private_key, energy, spark):
        self.validate_private_key(private_key)

        spark_token = self.web3.eth.contract(address=self.token_address, abi=self.token_abi)
        nonce = self.web3.eth.get_transaction_count(account)
        approval_txn = spark_token.functions.approve(self.trading_address, spark).build_transaction({
            'from': account,
            'nonce': nonce
        })

        signed_txn = self.web3.eth.account.sign_transaction(approval_txn, private_key=private_key)
        txn_hash = self.web3.eth.send_raw_transaction(signed_txn.raw_transaction)
        self.web3.eth.wait_for_transaction_receipt(txn_hash)

        nonce += 1

        tx = self.trading_contract.functions.addLiquidity(energy, spark).build_transaction({
            'from': account,
            'nonce': nonce,
            'gas': 2000000,
            'gasPrice': self.web3.to_wei('20', 'gwei')
        })

        signed_tx = self.web3.eth.account.sign_transaction(tx, private_key=private_key)
        tx_hash = self.web3.eth.send_raw_transaction(signed_tx.raw_transaction)
        receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)

        print(f"Liquidity added successfully. Receipt: {receipt}")
        return receipt
