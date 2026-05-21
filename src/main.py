import argparse
import sys

import boto3

from src.app import run


def main():
    parser = argparse.ArgumentParser(description="TUI for Amazon DocumentDB")
    parser.add_argument("--profile", help="AWS profile name")
    parser.add_argument("--region", help="AWS region name")
    args = parser.parse_args()

    session_kwargs = {}
    if args.profile:
        session_kwargs["profile_name"] = args.profile
    if args.region:
        session_kwargs["region_name"] = args.region

    try:
        session = boto3.Session(**session_kwargs)
    except Exception as e:
        print(f"Failed to create AWS session: {e}", file=sys.stderr)
        sys.exit(1)

    run(session)


if __name__ == "__main__":
    main()
