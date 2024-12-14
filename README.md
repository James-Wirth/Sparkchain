# Sparkchain⚡

![image](https://github.com/user-attachments/assets/dd484e1c-debe-415c-8dd4-4c6d66840218)

## Warning!

This project is under active development. 

## Setup

### Prerequisites

 - Python (3.7+)
 - Node.js and NPM
 - Ganache (CLI or UI)
 - Solidarity compiler (`solc`)

### Install Dependencies

Install Python packages:

```python
pip install -r requirements.txt
```

### Deploy Smart Contracts

Clone the repository:

```python
git clone https://github.com/James-Wirth/Sparkchain.git
cd Sparkchain
```

Run the following bash script to start ganache and deploy the smart contracts (saved to `deployment.json`):

```bash
bash scripts/load_ganache
```


## Technical Overview

### 1. Blockchain Smart Contracts:

**EnergyTrading.sol**: A Solidarity-based smart contract for energy trading, managing offers & bids, executing trades, and providing an Automated Market Maker (AMM) for energy pricing.

**SPARKToken.sol**: An ERC20-based utility token which is used on the exchange.





