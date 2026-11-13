#!/usr/bin/env python3
"""Fetch Google Scholar metrics and update the static site's JSON snapshot."""

from __future__ import annotations

import argparse
import json
import os
from datetime import date
from pathlib import Path
from typing import Any, Dict


REQUIRED_METRICS = {
    "citedby": "citations",
    "hindex": "hIndex",
    "i10index": "i10Index",
}


def _metric_value(author: Dict[str, Any], key: str) -> int:
    value = author.get(key)
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError("Google Scholar returned an invalid {} metric".format(key))
    return value


def build_snapshot(author: Dict[str, Any], profile_id: str, updated_at: str) -> Dict[str, Any]:
    """Build a complete, validated JSON-serializable Scholar snapshot."""
    profile_id = profile_id.strip()
    updated_at = updated_at.strip()
    if not profile_id:
        raise ValueError("Google Scholar profile ID is required")
    if not updated_at:
        raise ValueError("Snapshot date is required")

    snapshot = {
        "profileId": profile_id,
        "updatedAt": updated_at,
    }
    for source_key, output_key in REQUIRED_METRICS.items():
        snapshot[output_key] = _metric_value(author, source_key)
    return snapshot


def write_snapshot(snapshot: Dict[str, Any], output_path: Path) -> None:
    """Write a valid snapshot atomically so a failed run cannot truncate it."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = output_path.with_suffix(output_path.suffix + ".tmp")
    temp_path.write_text(
        json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temp_path.replace(output_path)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "data" / "scholar.json",
        help="Path to the static JSON snapshot.",
    )
    args = parser.parse_args()

    profile_id = os.environ.get("GOOGLE_SCHOLAR_USER_ID", "").strip()
    if not profile_id:
        raise SystemExit("GOOGLE_SCHOLAR_USER_ID is required")

    try:
        from scholarly import scholarly
    except ImportError as error:
        raise SystemExit("Install the pinned scholarly dependency before running this script") from error

    print("Fetching Google Scholar profile {}...".format(profile_id))
    author = scholarly.search_author_id(profile_id)
    scholarly.fill(author, sections=["indices"])
    snapshot = build_snapshot(author, profile_id, date.today().isoformat())
    write_snapshot(snapshot, args.output)
    print(
        "Updated {} citations, h-index {}, i10-index {}.".format(
            snapshot["citations"], snapshot["hIndex"], snapshot["i10Index"]
        )
    )


if __name__ == "__main__":
    main()
