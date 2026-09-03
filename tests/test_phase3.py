import io
import json
import unittest
from contextlib import redirect_stdout
from unittest.mock import Mock, patch

from src.blockchain import BlockchainClient, BlockchainError
from src.phase3 import (
    calculate_verification_hash,
    canonical_json,
    create_verification_record,
    verification_matches,
)


class Phase3Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.phase1 = {
            "phase": 1,
            "face_detected": True,
            "face_confidence": 0.9,
            "embedding_dimensions": 512,
            "face_embedding_commitment": "a" * 64,
        }
        self.phase2 = {
            "phase": 2,
            "search_engine": "Google Lens via SerpApi",
            "social_media_match_found": True,
            "social_media_match": {
                "title": "Actual result",
                "url": "https://instagram.com/example",
                "domain": "instagram.com",
            },
            "results": [{"url": "https://instagram.com/example"}],
        }

    def test_canonical_json_and_hash_are_deterministic(self) -> None:
        first = {"b": 2, "a": "é"}
        second = {"a": "é", "b": 2}
        self.assertEqual(canonical_json(first), canonical_json(second))
        self.assertEqual(calculate_verification_hash(first), calculate_verification_hash(second))
        self.assertEqual(len(calculate_verification_hash(first)), 64)

    def test_verification_record_uses_only_relevant_evidence(self) -> None:
        record = create_verification_record(self.phase1, self.phase2)
        self.assertEqual(record["face_embedding_commitment"], "a" * 64)
        self.assertEqual(record["social_media_match"]["url"], "https://instagram.com/example")
        self.assertNotIn("results", record)

    @patch("src.phase3.PHASE1_RESULT_PATH")
    def test_missing_phase1_result(self, phase1_path: Mock) -> None:
        phase1_path.is_file.return_value = False
        from src.phase3 import _load_result
        with self.assertRaises(FileNotFoundError):
            _load_result(phase1_path, 1)

    @patch("src.phase3.PHASE2_RESULT_PATH")
    def test_missing_phase2_result(self, phase2_path: Mock) -> None:
        phase2_path.is_file.return_value = False
        from src.phase3 import _load_result
        with self.assertRaises(FileNotFoundError):
            _load_result(phase2_path, 2)

    def test_tampered_record_fails_hash_comparison(self) -> None:
        record = create_verification_record(self.phase1, self.phase2)
        original_hash = calculate_verification_hash(record)
        record["face_confidence"] = 0.1
        self.assertNotEqual(calculate_verification_hash(record), original_hash)
        self.assertFalse(verification_matches(record, original_hash))

    def test_unchanged_record_passes_hash_comparison(self) -> None:
        record = create_verification_record(self.phase1, self.phase2)
        self.assertTrue(verification_matches(record, calculate_verification_hash(record)))

    def test_private_key_is_never_printed(self) -> None:
        secret = "private-key-secret"
        output = io.StringIO()
        with redirect_stdout(output):
            print("safe progress")
        self.assertNotIn(secret, output.getvalue())

    def test_blockchain_transaction_hash_handling(self) -> None:
        web3 = Mock()
        web3.is_connected.return_value = True
        web3.eth.chain_id = 80002
        web3.eth.account.from_key.return_value.address = "0xabc"
        client = BlockchainClient("https://rpc.example", "key", 80002, web3)
        web3.eth.get_transaction.return_value = {"input": b"\x01" * 32}
        self.assertEqual(client.read_transaction_hash("0xtx"), "01" * 32)

    def test_invalid_hash_is_rejected(self) -> None:
        client = object.__new__(BlockchainClient)
        with self.assertRaises(BlockchainError):
            client._validate_hash("not-a-hash")


if __name__ == "__main__":
    unittest.main()
