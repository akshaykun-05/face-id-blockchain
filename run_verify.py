"""Verify the local record against the hash stored in a blockchain transaction."""

import json

from src.blockchain import BlockchainClient
from src.phase3 import PROOF_PATH, RECORD_PATH, calculate_verification_hash, verification_matches


if __name__ == "__main__":
    try:
        record = json.loads(RECORD_PATH.read_text(encoding="utf-8"))
        proof = json.loads(PROOF_PATH.read_text(encoding="utf-8"))
        local_hash = calculate_verification_hash(record)
        blockchain_hash = BlockchainClient().read_transaction_hash(
            proof["transaction_hash"]
        )
        print("============================================================")
        print("              BLOCKCHAIN VERIFICATION")
        print("============================================================\n")
        print(f"Local hash      : {local_hash}")
        print(f"Blockchain hash : {blockchain_hash}\n")
        if (
            verification_matches(record, blockchain_hash)
            and local_hash == proof.get("verification_hash")
        ):
            print("Result          : VERIFIED")
            print("\nThe local verification record matches the")
            print("hash anchored on the blockchain.")
            raise SystemExit(0)
        print("Result          : VERIFICATION FAILED")
        print("\nThe local verification record does not match")
        print("the blockchain proof.")
        raise SystemExit(1)
    except SystemExit:
        raise
    except Exception as error:
        print(f"ERROR: {error}")
        raise SystemExit(1)
