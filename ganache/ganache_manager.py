import json
import os

class GanacheManager:
    def __init__(self, keys_file=None):
        if keys_file is None:
            keys_file = os.path.join(os.path.dirname(__file__), "ganache_keys.json")

        self.keys_file = keys_file
        self.accounts = self._load_accounts()

    def _load_accounts(self):
        with open(self.keys_file, "r") as file:
            data = json.load(file)
        return data["accounts"]

    def get_account(self, index):
        if index < 0 or index >= len(self.accounts):
            raise IndexError("Account index out of range.")
        return self.accounts[index]

    def get_all_accounts(self):
        return self.accounts
