import logging
import json
from typing import Dict
from cryptography.fernet import Fernet
import os

# Configure logging for transparency
logging.basicConfig(
    filename="trading_bot.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

class KeyStorage:
    def __init__(self):
        """Initialize secure key storage with Fernet encryption."""
        self.key = Fernet.generate_key()
        self.cipher = Fernet(self.key)
        self.keys_file = "keys.encrypted"
        self.accounts: Dict[str, Dict] = {}
        self.load_keys()
        logging.info("KeyStorage initialized")

    def load_keys(self):
        """Load encrypted keys from file with error handling."""
        if not os.path.exists(self.keys_file):
            return
        try:
            with open(self.keys_file, "rb") as f:
                self.accounts = json.loads(self.cipher.decrypt(f.read()).decode())
            logging.debug("Encrypted keys loaded successfully")
        except Exception as e:
            logging.error(f"Failed to load encrypted keys: {e}")

    def add_account(self, alias: str, wallet_address: str, private_key: str):
        """Add a new account with encrypted storage."""
        try:
            self.accounts[alias] = {"wallet_address": wallet_address, "private_key": private_key}
            self.save_keys()
            logging.info(f"Account added: {alias}")
        except Exception as e:
            logging.error(f"Failed to add account: {e}")

    def save_keys(self):
        """Save accounts to encrypted file."""
        try:
            with open(self.keys_file, "wb") as f:
                f.write(self.cipher.encrypt(json.dumps(self.accounts).encode()))
            logging.debug("Encrypted keys saved successfully")
        except Exception as e:
            logging.error(f"Failed to save encrypted keys: {e}")

# Example usage (incomplete, for demo only)
if __name__ == "__main__":
    storage = KeyStorage()
    storage.add_account("test_account", "0xYourWalletAddress", "YourPrivateKey")
    print(f"Stored accounts: {storage.accounts}")
