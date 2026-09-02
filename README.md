# Face ID + Blockchain Verification

This hackathon project implements **Phase 1 only**: image-based face detection, face encoding, normalization, and a SHA-256 cryptographic commitment.

> Phase 1 detects and encodes a face. Reverse-image search and blockchain verification are implemented in later phases.

The project is intended for demonstrations using an image of yourself or another consenting participant. It does not attempt to identify a person. The raw face embedding stays in memory and is never written to JSON, logs, terminal output, or a blockchain. SHA-256 is an integrity/commitment representation, not encryption, and does not make biometric data anonymous or fully irreversible.

## Project structure

```text
face-id-blockchain/
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── face_detector.py
│   ├── face_encoder.py
│   └── phase1.py
├── data/input/.gitkeep
├── data/output/.gitkeep
├── tests/test_phase1.py
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
└── run_phase1.py
```

## Installation on Windows

From the `face-id-blockchain` directory, create and activate a virtual environment:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks activation, run this once in PowerShell as your user:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Configuration

Copy `.env.example` to `.env`:

```powershell
Copy-Item .env.example .env
```

The defaults are `buffalo_l`, CPU execution through `CPUExecutionProvider`, a `640 x 640` detection size, and a `0.50` confidence threshold. You can edit `.env` to change the model name, detection size, or threshold.

## Run Phase 1

Put a test image from a consenting participant at `data/input/test.jpg`, then run:

```powershell
python run_phase1.py --image data/input/test.jpg
```

The command reports four steps, the selected face confidence, embedding dimension, and the 64-character commitment. It never prints the raw embedding.

Successful output is followed by:

```text
PHASE 1 COMPLETE
Face confidence : 0.9873
Embedding size  : 512
Commitment      : <64 hexadecimal characters>
Face crop saved : data/output/detected_face.jpg
Result saved    : data/output/phase1_result.json
```

A first run may download the InsightFace `buffalo_l` model pack and cache it locally. This requires internet access and can take some time. Later runs reuse the local model cache.

## Generated files

After a successful run, `data/output/` contains:

- `detected_face.jpg`: the clamped crop of the highest-confidence detected face.
- `phase1_result.json`: verification metadata and the SHA-256 commitment only.

Generated outputs are ignored by Git.

## Run tests

The unit tests do not require a face image or an InsightFace model download:

```powershell
python -m unittest discover -s tests -v
```
