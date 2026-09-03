"""Command-line entry point for Phase 3."""

from src.phase3 import run_phase3


if __name__ == "__main__":
    try:
        run_phase3()
    except Exception as error:
        print(f"ERROR: {error}")
        raise SystemExit(1)
