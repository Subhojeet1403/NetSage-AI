#!/usr/bin/env python3

"""Deterministic verifier for the NetSage AI diagnostic case library.

The checker intentionally uses conservative regex/rule matching. It does not
execute Cisco commands. It reads cases.csv and flags three concrete categories:
  * Layer 1 administrative-down interfaces
  * Layer 2 trunking failures
  * Layer 3 missing routing-table entries
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path


ADMIN_DOWN_PATTERNS = [
    re.compile(r"\b(?:administratively\s+down|admin(?:istratively)?\s+down)\b", re.I),
    re.compile(r"\bStatus:\s*administratively\s+down\b", re.I),
]

TRUNK_FAILURE_PATTERNS = [
    re.compile(r"Operational Mode:\s*(?:static access|access)\b", re.I),
    re.compile(r"switchport mode access", re.I),
    re.compile(r"switchport trunk allowed vlan\s+(?:none|remove)", re.I),
    re.compile(r"\btrunk\b.*\b(?:down|disabled|not\s+trunking|failure)\b", re.I),
    re.compile(r"\b(?:not\s+trunking|trunking\s+failed)\b", re.I),
]

MISSING_ROUTE_PATTERNS = [
    re.compile(r"%\s*(?:Network|Route|Routing entry)\s+not\s+in\s+table", re.I),
    re.compile(r"\bno\s+(?:route|routing\s+entry)\b", re.I),
    re.compile(r"\bmissing\s+(?:route|routing\s+table\s+entry)\b", re.I),
]


def read_cases(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    required = {
        "case_id", "domain_tag", "symptom", "topology_note",
        "show_outputs", "expected_fault", "osi_layer", "severity"
    }
    if not rows:
        raise ValueError("cases.csv contains no data rows")
    if set(rows[0]) != required:
        raise ValueError(
            "cases.csv columns do not match the required schema: "
            + ", ".join(sorted(required))
        )
    return rows


def flag_patterns(text: str, patterns: list[re.Pattern[str]]) -> bool:
    return any(pattern.search(text) for pattern in patterns)


def diagnose(row: dict[str, str]) -> list[str]:
    evidence = f"{row['show_outputs']}\n{row['expected_fault']}\n{row['symptom']}"
    flags: list[str] = []

    if flag_patterns(evidence, ADMIN_DOWN_PATTERNS):
        flags.append("L1_ADMINISTRATIVELY_DOWN")

    if flag_patterns(evidence, TRUNK_FAILURE_PATTERNS):
        flags.append("L2_TRUNKING_FAILURE")

    if flag_patterns(evidence, MISSING_ROUTE_PATTERNS):
        flags.append("L3_MISSING_ROUTE")

    return flags


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify NetSage AI troubleshooting cases with deterministic rules."
    )
    parser.add_argument(
        "csv_file",
        nargs="?",
        default=str(Path(__file__).with_name("cases.csv")),
        help="Path to cases.csv (default: adjacent cases.csv)",
    )
    args = parser.parse_args()

    try:
        rows = read_cases(Path(args.csv_file))
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print(f"Loaded {len(rows)} case(s).")
    total_flags = 0
    for row in rows:
        flags = diagnose(row)
        if flags:
            total_flags += len(flags)
            print(f"{row['case_id']}: {', '.join(flags)}")
        else:
            print(f"{row['case_id']}: no deterministic flags")

    print(f"Total deterministic flags: {total_flags}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
