"""Command-line entry point for Phase 2."""

import argparse

from src.phase2 import run_phase2


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Face ID Phase 2")
    parser.add_argument("--image", required=True, help="Path to the input image")
    args = parser.parse_args()

    print("============================================================")
    print("       FACE ID + BLOCKCHAIN VERIFICATION")
    print("                  PHASE 2")
    print("============================================================\n")
    try:
        run_phase2(args.image)
    except Exception as error:
        print(f"ERROR: {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
