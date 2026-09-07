"""Minimal Web3 client for anchoring a verification hash on an EVM testnet."""

import os
from datetime import datetime, timezone
from typing import Any

from dotenv import load_dotenv

from .config import PROJECT_ROOT

load_dotenv(PROJECT_ROOT / ".env")


class BlockchainError(RuntimeError):
    """Raised when blockchain configuration or operations fail."""


class BlockchainClient:
    """Submit and inspect hash-only transactions without exposing credentials."""

    def __init__(
        self,
        rpc_url: str | None = None,
        private_key: str | None = None,
        chain_id: int | str | None = None,
        web3_instance: Any | None = None,
    ) -> None:
        self.rpc_url = rpc_url or os.getenv("BLOCKCHAIN_RPC_URL")
        self.private_key = private_key or os.getenv("BLOCKCHAIN_PRIVATE_KEY")
        configured_chain_id = chain_id or os.getenv("BLOCKCHAIN_CHAIN_ID")
        if not self.rpc_url:
            raise BlockchainError("BLOCKCHAIN_RPC_URL is missing. Add it to .env.")
        if not self.private_key:
            raise BlockchainError("BLOCKCHAIN_PRIVATE_KEY is missing. Add it to .env.")
        try:
            self.chain_id = int(configured_chain_id)  # type: ignore[arg-type]
        except (TypeError, ValueError) as error:
            raise BlockchainError(
                "BLOCKCHAIN_CHAIN_ID must be a valid integer."
            ) from error
        if self.chain_id <= 0:
            raise BlockchainError("BLOCKCHAIN_CHAIN_ID must be positive.")

        try:
            if web3_instance is None:
                from web3 import Web3

                self.web3 = Web3(Web3.HTTPProvider(self.rpc_url))
            else:
                self.web3 = web3_instance
            if not self.web3.is_connected():
                raise BlockchainError("Could not connect to blockchain RPC.")
            self.account = self.web3.eth.account.from_key(self.private_key)
        except BlockchainError:
            raise
        except Exception as error:
            raise BlockchainError("Invalid blockchain configuration or private key.") from error

        try:
            remote_chain_id = int(self.web3.eth.chain_id)
        except Exception as error:
            raise BlockchainError("Could not read blockchain chain ID.") from error
        if remote_chain_id != self.chain_id:
            raise BlockchainError(
                f"Configured chain ID {self.chain_id} does not match RPC chain ID {remote_chain_id}."
            )

    @staticmethod
    def _validate_hash(verification_hash: str) -> bytes:
        if len(verification_hash) != 64:
            raise BlockchainError("Verification hash must be 64 hexadecimal characters.")
        try:
            return bytes.fromhex(verification_hash)
        except ValueError as error:
            raise BlockchainError("Verification hash must be hexadecimal.") from error

    def submit_hash(self, verification_hash: str) -> dict[str, Any]:
        """Send a transaction whose data is exactly the 32-byte verification hash."""
        hash_bytes = self._validate_hash(verification_hash)
        try:
            from web3.exceptions import TimeExhausted

            nonce = self.web3.eth.get_transaction_count(self.account.address)
            transaction = {
                "from": self.account.address,
                "to": self.account.address,
                "value": 0,
                "nonce": nonce,
                "chainId": self.chain_id,
                "data": self.web3.to_hex(hash_bytes),
                "gas": 25_000,
                "gasPrice": self.web3.eth.gas_price,
            }
            signed = self.account.sign_transaction(transaction)
            transaction_hash = self.web3.eth.send_raw_transaction(
                signed.raw_transaction
            )
            receipt = self.web3.eth.wait_for_transaction_receipt(
                transaction_hash, timeout=120
            )
        except TimeExhausted as error:
            raise BlockchainError("Timed out waiting for blockchain confirmation.") from error
        except Exception as error:
            raise BlockchainError("Blockchain transaction failed.") from error

        if int(receipt.status) != 1:
            raise BlockchainError("Blockchain transaction was not confirmed successfully.")
        block_number = int(receipt.blockNumber)
        info: dict[str, Any] = {
            "transaction_hash": self.web3.to_hex(transaction_hash),
            "chain_id": self.chain_id,
            "verification_hash": verification_hash,
            "block_number": block_number,
            "confirmed": True,
        }
        try:
            block = self.web3.eth.get_block(block_number)
            timestamp = block.get("timestamp")
            if timestamp is not None:
                info["timestamp"] = datetime.fromtimestamp(
                    int(timestamp), tz=timezone.utc
                ).isoformat()
        except Exception:
            pass
        return info

    def read_transaction_hash(self, transaction_hash: str) -> str:
        """Read the 32-byte hash stored in transaction input data."""
        try:
            transaction = self.web3.eth.get_transaction(transaction_hash)
            data = transaction.get("input", transaction.get("data", b""))
            if isinstance(data, str):
                data = data[2:] if data.startswith("0x") else data
                data_bytes = bytes.fromhex(data)
            else:
                data_bytes = bytes(data)
        except Exception as error:
            raise BlockchainError("Could not read blockchain transaction.") from error
        if len(data_bytes) != 32:
            raise BlockchainError("Blockchain transaction does not contain a 32-byte hash.")
        return data_bytes.hex()
