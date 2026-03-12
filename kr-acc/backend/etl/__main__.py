"""CLI entry point for the ETL pipeline.

Usage:
    python -m etl full          # Run full sync
    python -m etl politicians   # Sync politicians only
    python -m etl bills         # Sync bills only
    python -m etl votes         # Sync votes only
    python -m etl co-sponsorship # Compute co-sponsorship edges
"""

import asyncio
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


def main() -> None:
    """Run ETL flow based on CLI argument."""
    from etl.flows import (
        compute_co_sponsorship,
        full_sync,
        sync_bills,
        sync_politicians,
        sync_votes,
    )

    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]
    flow_map = {
        "full": full_sync,
        "politicians": sync_politicians,
        "bills": sync_bills,
        "votes": sync_votes,
        "co-sponsorship": compute_co_sponsorship,
    }

    flow_fn = flow_map.get(command)
    if not flow_fn:
        print(f"Unknown command: {command}")
        print(f"Available: {', '.join(flow_map.keys())}")
        sys.exit(1)

    if asyncio.iscoroutinefunction(flow_fn.fn):
        asyncio.run(flow_fn())
    else:
        flow_fn()


if __name__ == "__main__":
    main()
