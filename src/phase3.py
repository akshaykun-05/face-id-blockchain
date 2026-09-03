"""Phase 3: create, hash, and anchor the Phase 1/2 verification record."""

import hashlib
import json
from pathlib import Path
from typing import Any

from .blockchain import BlockchainClient
from .config import PROJECT_ROOT

OUTPUT_DIR = PROJECT_ROOT / "data" / "output"
PHASE1_RESULT_PATH = OUTPUT_DIR / "phase1_result.json"
PHASE2_RESULT_PATH = OUTPUT_DIR / "phase2_result.json"
RECORD_PATH = OUTPUT_DIR / "verification_record.json"
HASH_PATH = OUTPUT_DIR / "verification_hash.json"
PROOF_PATH = OUTPUT_DIR / "blockchain_proof.json"


def canonical_json(record: dict[str, Any]) -> bytes:
    """Return deterministic UTF-8 JSON bytes for a verification record."""
    return json.dumps(
        record, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def calculate_verification_hash(record: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_json(record)).hexdigest()


def verification_matches(record: dict[str, Any], blockchain_hash: str) -> bool:
    """Return whether the local record hashes to the anchored blockchain value."""
    return calculate_verification_hash(record) == blockchain_hash


def _load_result(path: Path, phase: int) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"Phase {phase} result is missing: {path}")
    try:
        result = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"Phase {phase} result is malformed: {path}") from error
    if not isinstance(result, dict) or result.get("phase") != phase:
        raise ValueError(f"Phase {phase} result is invalid: {path}")
    return result


def create_verification_record(
    phase1_result: dict[str, Any], phase2_result: dict[str, Any]
) -> dict[str, Any]:
    record: dict[str, Any] = {"phase": 3}
    for field in (
        "face_embedding_commitment",
        "face_detected",
        "face_confidence",
        "embedding_dimensions",
    ):
        if field in phase1_result:
            record[field] = phase1_result[field]
    for field in ("search_engine", "social_media_match_found"):
        if field in phase2_result:
            record[field] = phase2_result[field]
    if isinstance(phase2_result.get("social_media_match"), dict):
        record["social_media_match"] = phase2_result["social_media_match"]
    return record


def run_phase3() -> dict[str, Any]:
    print("============================================================")
    print("       FACE ID + BLOCKCHAIN VERIFICATION")
    print("                  PHASE 3")
    print("============================================================\n")
    print("[1/5] Loading Phase 1 result...")
    phase1_result = _load_result(PHASE1_RESULT_PATH, 1)
    print("      OK Phase 1 result loaded")
    print("\n[2/5] Loading Phase 2 result...")
    phase2_result = _load_result(PHASE2_RESULT_PATH, 2)
    print("      OK Phase 2 result loaded")
    print("\n[3/5] Creating verification record...")
    record = create_verification_record(phase1_result, phase2_result)
    verification_hash = calculate_verification_hash(record)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    RECORD_PATH.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    HASH_PATH.write_text(
        json.dumps({"verification_hash": verification_hash}, indent=2) + "\n",
        encoding="utf-8",
    )
    print("      OK Verification record created")
    print(f"      SHA-256: {verification_hash}")
    print("\n[4/5] Anchoring verification hash on blockchain...")
    client = BlockchainClient()
    proof = client.submit_hash(verification_hash)
    print("      OK Transaction submitted")
    print("\n[5/5] Waiting for blockchain confirmation...")
    print("      OK Transaction confirmed")

    proof = {
        "phase": 3,
        "network": "Polygon Amoy",
        **{key: proof[key] for key in ("chain_id", "verification_hash", "transaction_hash", "block_number", "timestamp", "confirmed") if key in proof},
    }
    PROOF_PATH.write_text(json.dumps(proof, indent=2) + "\n", encoding="utf-8")
    print("\n------------------------------------------------------------")
    print("PHASE 3 COMPLETE")
    print("------------------------------------------------------------")
    print("\nBlockchain      : Polygon Amoy")
    print(f"Chain ID         : {proof['chain_id']}")
    print(f"Transaction hash : {proof['transaction_hash']}")
    print(f"Verification hash: {proof['verification_hash']}")
    print("\nRecord saved     : data/output/verification_record.json")
    print("Hash saved       : data/output/verification_hash.json")
    print("Proof saved      : data/output/blockchain_proof.json")
    return proof
