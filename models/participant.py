class Generator:
    def __init__(self, generator_id, energy_capacity, price_per_unit, address):
        self.generator_id = generator_id
        self.energy_capacity = energy_capacity
        self.price_per_unit = price_per_unit
        self.address = address

    def submit_offer(self, blockchain):
        tx = blockchain.trading_contract.functions.submitOffer(
            self.energy_capacity, self.price_per_unit
        ).transact({'from': self.address})
        receipt = blockchain.web3.eth.wait_for_transaction_receipt(tx)
        return receipt


class Supplier:
    def __init__(self, supplier_id, energy_demand, max_price_per_unit, address):
        self.supplier_id = supplier_id
        self.energy_demand = energy_demand
        self.max_price_per_unit = max_price_per_unit
        self.address = address

    def submit_bid(self, blockchain):
        tx = blockchain.trading_contract.functions.submitBid(
            self.energy_demand, self.max_price_per_unit
        ).transact({'from': self.address})
        receipt = blockchain.web3.eth.wait_for_transaction_receipt(tx)
        return receipt
