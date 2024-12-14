import dash
from dash import dcc, html, Input, Output, State, callback_context, dash_table
import plotly.graph_objects as go
from models.blockchain import Blockchain
from ganache.ganache_manager import GanacheManager
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

    try:
        blockchain.add_liquidity(
            ganache_manager.get_account(0)["address"],
            ganache_manager.get_account(0)["private_key"],
            energy=2000, spark=10000
        )
    except Exception as e:
        print(f"Failed to add liquidity: {e}")

    offers = blockchain.trading_contract.functions.getOffers().call()
    bids = blockchain.trading_contract.functions.getBids().call()

    optimizer = TradeMatcher(offers, bids)
    matched_trades = optimizer.optimize_matching()

    # Log details
    amm_price = blockchain.trading_contract.functions.getEnergyPrice().call()
    print(f"AMM Price: {amm_price} SPARK per unit of energy")

    trade_details = []
    for (offer_idx, bid_idx), trade_energy in matched_trades.items():
        try:
            offer = offers[offer_idx]
            bid = bids[bid_idx]
            trade_details.append({
                "generator_id": f"Gen-{offer[0]}",
                "supplier_id": f"Sup-{bid[0]}",
                "energy_exchanged": trade_energy,
                "price": offer[2]
            })
            print(f"Matched: Offer {offer_idx} -> Bid {bid_idx}, Energy: {trade_energy}")
        except Exception as e:
            print(f"Error processing trade: {e}")

    return trade_details

# Initialize the app
app = dash.Dash(__name__)
app.title = "Energy Trading Simulation"

# Blockchain setup
provider_url = "http://127.0.0.1:8545"
token_abi_path = os.path.join("contracts", "SPARKToken.abi")
trading_abi_path = os.path.join("contracts", "EnergyTrading.abi")

with open(os.path.join("scripts", "deployment.json"), "r") as file:
    deployment_data = json.load(file)

token_address = deployment_data["SPARKToken"]
trading_address = deployment_data["EnergyTrading"]
blockchain = Blockchain(provider_url, token_abi_path, token_address, trading_abi_path, trading_address)
ganache_manager = GanacheManager()

# Generate account dropdown options (excluding account 0)
accounts = [
    {"label": f"Account {i}: {ganache_manager.get_account(i)['address']}", "value": ganache_manager.get_account(i)['address']}
    for i in range(1, 10)
]

app.layout = html.Div([
    html.H1("Blockchain Energy Trading Simulation", style={"textAlign": "center"}),

    html.Div([
        html.H3("Fund Accounts"),
        dcc.Dropdown(id="fund-account-dropdown", options=accounts, placeholder="Select Account"),
        dcc.Input(id="fund-amount", type="number", placeholder="Amount (SPARK)", step=1),
        html.Button("Fund", id="fund-button", n_clicks=0),
        html.Div(id="fund-status")
    ], style={"marginBottom": "20px"}),

    html.Div([
        html.H3("Add Generator Offer"),
        dcc.Dropdown(id="gen-address-dropdown", options=accounts, placeholder="Select Generator Account"),
        dcc.Input(id="gen-energy", type="number", placeholder="Energy Capacity", step=1),
        dcc.Input(id="gen-price", type="number", placeholder="Price per Unit", step=0.01),
        html.Button("Add Offer", id="add-gen-button", n_clicks=0),
        html.Div(id="gen-status")
    ], style={"marginBottom": "20px"}),

    html.Div([
        html.H3("Add Supplier Bid"),
        dcc.Dropdown(id="sup-address-dropdown", options=accounts, placeholder="Select Supplier Account"),
        dcc.Input(id="sup-demand", type="number", placeholder="Energy Demand", step=1),
        dcc.Input(id="sup-max-price", type="number", placeholder="Max Price per Unit", step=0.01),
        html.Button("Add Bid", id="add-sup-button", n_clicks=0),
        html.Div(id="sup-status")
    ], style={"marginBottom": "20px"}),

    html.Div([
        html.Button("Run Matching Algorithm", id="run-matching-button", n_clicks=0),
        html.Div(id="matching-status")
    ], style={"marginBottom": "20px"}),

    html.Div([
        html.H3("Outstanding Orders (Order Book)"),
        dash_table.DataTable(id="order-book-table", columns=[
            {"name": "Order Type", "id": "order_type"},
            {"name": "Account", "id": "account"},
            {"name": "Energy", "id": "energy"},
            {"name": "Price (SPARK)", "id": "price"}
        ], style_table={"overflowX": "auto"})
    ], style={"marginBottom": "20px"}),

    html.Div([
        html.H3("Matched Trades"),
        dash_table.DataTable(id="trade-table", columns=[
            {"name": "Generator ID", "id": "generator_id"},
            {"name": "Supplier ID", "id": "supplier_id"},
            {"name": "Energy Exchanged", "id": "energy_exchanged"},
            {"name": "Price (SPARK)", "id": "price"}
        ], style_table={"overflowX": "auto"})
    ], style={"marginBottom": "20px"}),

    html.Div([
        html.H3("Current Funds"),
        dash_table.DataTable(id="funds-table", columns=[
            {"name": "Account", "id": "account"},
            {"name": "SPARK Balance", "id": "balance"}
        ], style_table={"overflowX": "auto"})
    ])
])

# Callbacks
@app.callback(
    Output("fund-status", "children"),
    Input("fund-button", "n_clicks"),
    State("fund-account-dropdown", "value"),
    State("fund-amount", "value")
)
def fund_account(n_clicks, account, amount):
    if n_clicks > 0:
        try:
            fund_accounts_with_spark(blockchain, [account], amount)
            return f"Account {account} funded with {amount} SPARK tokens."
        except Exception as e:
            return f"Error funding account: {e}"
    return ""

@app.callback(
    Output("gen-status", "children"),
    Input("add-gen-button", "n_clicks"),
    State("gen-address-dropdown", "value"),
    State("gen-energy", "value"),
    State("gen-price", "value")
)
def add_generator_offer(n_clicks, address, energy, price):
    if n_clicks > 0:
        try:
            generator = Generator(generator_id=f"Gen-{address[-4:]}", energy_capacity=energy, price_per_unit=price, address=address)
            generator.submit_offer(blockchain)
            return f"Generator {address} added an offer of {energy} units at {price} SPARK per unit."
        except Exception as e:
            return f"Error adding generator offer: {e}"
    return ""

@app.callback(
    Output("sup-status", "children"),
    Input("add-sup-button", "n_clicks"),
    State("sup-address-dropdown", "value"),
    State("sup-demand", "value"),
    State("sup-max-price", "value")
)
def add_supplier_bid(n_clicks, address, demand, max_price):
    if n_clicks > 0:
        if not address:
            return "Error: Please select a supplier account."
        if demand is None or max_price is None:
            return "Error: Please enter valid values for demand and max price."
        try:
            supplier = Supplier(
                supplier_id=f"Sup-{address[-4:]}",
                energy_demand=demand,
                max_price_per_unit=max_price,
                address=address
            )
            supplier.submit_bid(blockchain)
            return f"Supplier {address} added a bid for {demand} units at max {max_price} SPARK per unit."
        except Exception as e:
            return f"Error adding supplier bid: {e}"
    return ""

@app.callback(
    [Output("matching-status", "children"), Output("trade-table", "data")],
    Input("run-matching-button", "n_clicks")
)
def run_matching_algorithm(n_clicks):
    if n_clicks > 0:
        try:
            trade_details = run_simulation()

            # Check if there are any matches
            if not trade_details:
                return "No trades matched.", []

            return "Matching completed successfully!", trade_details
        except Exception as e:
            return f"Error running matching algorithm: {e}", []

    return "", []

@app.callback(
    Output("funds-table", "data"),
    Input("run-matching-button", "n_clicks")
)
def update_funds_table(n_clicks):
    try:
        funds_data = [
            {"account": f"Account {i}: {ganache_manager.get_account(i)['address']}",
             "balance": blockchain.token_contract.functions.balanceOf(ganache_manager.get_account(i)['address']).call()}
            for i in range(1, 10)  # Exclude account 0
        ]
        return funds_data
    except Exception as e:
        return []

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
