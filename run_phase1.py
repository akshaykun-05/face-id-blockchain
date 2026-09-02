"""Command-line entry point for Phase 1."""

import argparse

from src.phase1 import run_phase1


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Face ID Phase 1")
    parser.add_argument("--image", required=True, help="Path to the input image")
    args = parser.parse_args()

    print("============================================================")
    print("       FACE ID + BLOCKCHAIN VERIFICATION")
    print("                  PHASE 1")
    print("============================================================\n")
    try:
        run_phase1(args.image)
    except Exception as error:
        print(f"ERROR: {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
