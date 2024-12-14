![image](https://github.com/user-attachments/assets/5392b0b0-7d26-41a3-ad54-d5c006b84140)# Sparkchain⚡

## Warning!

This project is under active development. 

![image](https://github.com/user-attachments/assets/fd163728-fa18-47fe-83e9-bb2cebe74fcc)

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





