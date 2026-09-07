# Face ID + Blockchain Verification

This hackathon project runs a three-phase verification flow:

1. Phase 1 detects a face and creates a SHA-256 face-embedding commitment.
2. Phase 2 performs a genuine Google Lens reverse-image search through SerpApi.
3. Phase 3 creates a verification record, hashes it, and anchors that SHA-256 hash on the Polygon Amoy testnet.

Use an image of yourself or another consenting participant. The raw face embedding is never written to JSON, printed, or placed on-chain. A SHA-256 commitment is an integrity representation, not encryption or a guarantee of anonymity.

## Prerequisites

- Python 3.11
- pip
- Git
- A SerpApi account and API key for Google Lens
- An EVM wallet for Polygon Amoy
- A Polygon Amoy RPC endpoint
- Testnet POL in the wallet for gas

## Installation

From the `face-id-blockchain` directory:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Environment Setup

Copy the template to a local `.env` file:

```powershell
Copy-Item .env.example .env
```

Edit `.env` with your own local credentials:

```env
SERPAPI_API_KEY=
BLOCKCHAIN_RPC_URL=
BLOCKCHAIN_PRIVATE_KEY=
BLOCKCHAIN_CHAIN_ID=80002
```

Variables:

- `SERPAPI_API_KEY`: Your SerpApi key for the Google Lens request.
- `BLOCKCHAIN_RPC_URL`: Your Polygon Amoy JSON-RPC endpoint.
- `BLOCKCHAIN_PRIVATE_KEY`: The private key for the funded testnet wallet used to submit the transaction.
- `BLOCKCHAIN_CHAIN_ID`: Polygon Amoy, which is `80002`.

`.env` is local only and must not be committed. `.env.example` contains placeholders only.

## Run The Complete Project

Place a consenting participant's image at `data/input/YOUR_IMAGE.jpg`, then run:

```powershell
python run_phase1.py --image data/input/YOUR_IMAGE.jpg
python run_phase2.py --image data/input/YOUR_IMAGE.jpg
python run_phase3.py
python run_verify.py
```

### Phase 1

```powershell
python run_phase1.py --image data/input/YOUR_IMAGE.jpg
```

This saves the Phase 1 result and a face-embedding commitment without saving the raw embedding.

### Phase 2

```powershell
python run_phase2.py --image data/input/YOUR_IMAGE.jpg
```

This sends the image to Google Lens through SerpApi, processes the real returned results, identifies matching social-media results, and saves the selected result as search evidence.

### Phase 3

```powershell
python run_phase3.py
```

Phase 3 loads the Phase 1 and Phase 2 results, creates the verification record, calculates its SHA-256 hash, submits only that hash as transaction data to Polygon Amoy, waits for confirmation, and saves the blockchain proof.

### Verification

```powershell
python run_verify.py
```

Verification recalculates the local record hash, retrieves the real blockchain transaction, extracts the anchored hash, and prints `VERIFIED` when they match.

## Tamper Test

1. Run `python run_verify.py` with the original verification record. It should produce `VERIFIED`.
2. Temporarily change a value in `data/output/verification_record.json`.
3. Run `python run_verify.py` again. It should produce `VERIFICATION FAILED`.
4. Restore the original verification record afterward.

Do not make a real blockchain transaction from the test suite.

## Tests

Run:

```powershell
python -m pytest
```

The expected current result is `17 passed`. The tests use mocked blockchain behavior where needed and do not submit real transactions.

## Security / Secrets

- The real `.env` is intentionally excluded from GitHub by `.gitignore`.
- Private keys, API keys, and RPC credentials must never be committed.
- Evaluators must provide their own credentials locally in `.env`.
- `.env.example` contains placeholders only.
- Phase 3 anchors only the SHA-256 verification hash; it does not put the raw face embedding on-chain.

The normal GitHub Actions workflow runs tests only and does not submit real blockchain transactions.
