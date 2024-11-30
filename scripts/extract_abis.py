import json
import os

def extract_abi(input_path, output_path):
    with open(input_path, 'r') as infile:
        contract_data = json.load(infile)
        abi = contract_data['abi']
    with open(output_path, 'w') as outfile:
        json.dump(abi, outfile, indent=4)
    print(f"ABI extracted to {output_path}")

# Paths to artifacts and output
artifacts_dir = "../artifacts/contracts/"
contracts = [
    {"input": f"{artifacts_dir}SPARKToken.sol/SPARKToken.json", "output": "../contracts/SPARKToken.abi"},
    {"input": f"{artifacts_dir}EnergyTrading.sol/EnergyTrading.json", "output": "../contracts/EnergyTrading.abi"},
]

# Extract ABIs
for contract in contracts:
    extract_abi(contract['input'], contract['output'])
