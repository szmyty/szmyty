"""
validate_evidence.py
====================
Validate ``profile/content/evidence.yml`` against the evidence schema.

Rules
-----
- Every record must have all required fields.
- No unknown fields are permitted.
- ``status`` must be one of: ``verified``, ``needs-user-verification``,
  ``excluded``.
- ``sensitivity`` must be one of: ``public``, ``sensitive``, ``internal``.
- ``evidence_type`` must be one of: ``url``, ``repo-path``, ``self-reported``,
  ``inferred``, ``none``.
- Records with ``status: needs-user-verification`` are flagged but NOT
  considered an error; they must not be auto-published.
- Sensitive values (``url``, ``claim``) are never printed to stdout.
- Exits with code 0 on success, 1 on validation failure.

Usage
-----
    python profile/validate_evidence.py [path/to/evidence.yml]
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    sys.exit(
        "Error: PyYAML is required.  Install it with: pip install pyyaml\n"
        f"Details: {exc}"
    )

# ---------------------------------------------------------------------------
# Schema definition
# ---------------------------------------------------------------------------

REQUIRED_FIELDS: frozenset[str] = frozenset(
    {
        "id",
        "claim",
        "evidence_type",
        "status",
        "sensitivity",
        "last_reviewed",
    }
)

OPTIONAL_FIELDS: frozenset[str] = frozenset({"url", "repo_path", "notes"})

ALLOWED_FIELDS: frozenset[str] = REQUIRED_FIELDS | OPTIONAL_FIELDS

VALID_STATUSES: frozenset[str] = frozenset(
    {"verified", "needs-user-verification", "excluded"}
)

VALID_SENSITIVITIES: frozenset[str] = frozenset({"public", "sensitive", "internal"})

VALID_EVIDENCE_TYPES: frozenset[str] = frozenset(
    {"url", "repo-path", "self-reported", "inferred", "none"}
)

# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------


def _safe_id(record: Any) -> str:
    """Return the record ID or a placeholder without printing sensitive data."""
    if isinstance(record, dict):
        raw = record.get("id")
        if isinstance(raw, str) and raw.strip():
            return raw.strip()
    return "<unknown-record>"


def validate_record(record: Any, index: int) -> list[str]:
    """Return a list of error strings for *record* (empty means valid)."""
    errors: list[str] = []

    if not isinstance(record, dict):
        errors.append(
            f"Record {index}: expected a mapping, got {type(record).__name__}"
        )
        return errors

    record_id = _safe_id(record)
    prefix = f"Record '{record_id}' (index {index})"

    # Unknown fields — print sorted field names only (not values) to stderr
    unknown = set(record.keys()) - ALLOWED_FIELDS
    if unknown:
        errors.append(f"{prefix}: unknown field(s): {sorted(unknown)}")

    # Required fields
    for field in sorted(REQUIRED_FIELDS):
        if field not in record:
            errors.append(f"{prefix}: missing required field '{field}'")
        elif not isinstance(record[field], str) or not record[field].strip():
            errors.append(f"{prefix}: field '{field}' must be a non-empty string")

    # Controlled vocabulary checks (only when the field is present and a string)
    status = record.get("status")
    if isinstance(status, str) and status not in VALID_STATUSES:
        errors.append(
            f"{prefix}: invalid status '{status}'; "
            f"must be one of {sorted(VALID_STATUSES)}"
        )

    sensitivity = record.get("sensitivity")
    if isinstance(sensitivity, str) and sensitivity not in VALID_SENSITIVITIES:
        errors.append(
            f"{prefix}: invalid sensitivity '{sensitivity}'; "
            f"must be one of {sorted(VALID_SENSITIVITIES)}"
        )

    evidence_type = record.get("evidence_type")
    if isinstance(evidence_type, str) and evidence_type not in VALID_EVIDENCE_TYPES:
        errors.append(
            f"{prefix}: invalid evidence_type '{evidence_type}'; "
            f"must be one of {sorted(VALID_EVIDENCE_TYPES)}"
        )

    # Sensitive records must not carry a public url
    if sensitivity == "sensitive" and record.get("url"):
        errors.append(
            f"{prefix}: sensitive record must not have a 'url' field "
            "(would expose private data)"
        )

    return errors


def validate_file(path: Path) -> int:
    """
    Validate *path* and write a report to stdout.

    Returns 0 on success, 1 on failure.
    """
    if not path.exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        return 1

    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        print(f"Error: YAML parse error in {path}:\n  {exc}", file=sys.stderr)
        return 1

    if not isinstance(raw, dict):
        print(
            f"Error: {path} must be a YAML mapping at the top level.",
            file=sys.stderr,
        )
        return 1

    records = raw.get("records")
    if records is None:
        print(f"Error: {path} has no 'records' key.", file=sys.stderr)
        return 1

    if not isinstance(records, list):
        print(f"Error: 'records' in {path} must be a list.", file=sys.stderr)
        return 1

    all_errors: list[str] = []
    unresolved_ids: list[str] = []
    excluded_ids: list[str] = []
    seen_ids: set[str] = set()
    duplicate_ids: list[str] = []

    for index, record in enumerate(records):
        # Duplicate ID check
        record_id = _safe_id(record)
        if record_id != "<unknown-record>":
            if record_id in seen_ids:
                duplicate_ids.append(record_id)
            seen_ids.add(record_id)

        errors = validate_record(record, index)
        all_errors.extend(errors)

        if isinstance(record, dict):
            status = record.get("status")
            if status == "needs-user-verification":
                unresolved_ids.append(record_id)
            elif status == "excluded":
                excluded_ids.append(record_id)

    for dup in duplicate_ids:
        all_errors.append(f"Duplicate record ID: '{dup}'")

    # Report
    total = len(records)
    verified = sum(
        1 for r in records if isinstance(r, dict) and r.get("status") == "verified"
    )

    print(f"Evidence catalog: {path}")
    print(f"  Total records  : {total}")
    print(f"  Verified       : {verified}")
    print(f"  Needs review   : {len(unresolved_ids)}")
    print(f"  Excluded       : {len(excluded_ids)}")

    if unresolved_ids:
        print("\nUnresolved claims (needs-user-verification):")
        for rid in unresolved_ids:
            print(f"  - {rid}")

    if excluded_ids:
        print("\nExcluded records (not for publication):")
        for rid in excluded_ids:
            print(f"  - {rid}")

    if all_errors:
        print(f"\nValidation FAILED — {len(all_errors)} error(s):", file=sys.stderr)
        for err in all_errors:
            print(f"  ERROR: {err}", file=sys.stderr)
        return 1

    print("\nValidation passed.")
    return 0


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> int:
    default_path = Path(__file__).parent / "content" / "evidence.yml"
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else default_path
    return validate_file(path)


if __name__ == "__main__":
    sys.exit(main())
