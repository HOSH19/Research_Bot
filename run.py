import argparse
from agent import run_agent

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Newsletter Digest Agent")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print digest to stdout instead of sending to Telegram",
    )
    args = parser.parse_args()

    run_agent(dry_run=args.dry_run)
