"""
Tests for profile/validate_evidence.py.
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest
import yaml

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# Import the module under test by path so we don't need an installed package.
import importlib.util
import sys


def _load_validator():
    spec = importlib.util.spec_from_file_location(
        "validate_evidence",
        Path(__file__).parents[1] / "profile" / "validate_evidence.py",
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


validator = _load_validator()
validate_record = validator.validate_record
validate_file = validator.validate_file


def _write_catalog(tmp_path: Path, records: list[dict]) -> Path:
    """Write a minimal valid catalog YAML file to *tmp_path* and return the path."""
    data = {"schema_version": "1", "records": records}
    p = tmp_path / "evidence.yml"
    p.write_text(yaml.dump(data, allow_unicode=True), encoding="utf-8")
    return p


def _valid_record(**overrides) -> dict:
    """Return a fully-valid record dict, applying any *overrides*."""
    base = {
        "id": "test-record",
        "claim": "Test claim",
        "evidence_type": "url",
        "url": "https://example.com",
        "status": "verified",
        "sensitivity": "public",
        "last_reviewed": "2026-08-09",
    }
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# validate_record — accepted records
# ---------------------------------------------------------------------------


class TestValidateRecordAccepted:
    def test_minimal_valid_record(self):
        record = {
            "id": "test-id",
            "claim": "Some claim",
            "evidence_type": "none",
            "status": "verified",
            "sensitivity": "public",
            "last_reviewed": "2026-01-01",
        }
        assert validate_record(record, 0) == []

    def test_verified_with_url(self):
        assert validate_record(_valid_record(), 0) == []

    def test_needs_user_verification(self):
        record = _valid_record(status="needs-user-verification")
        assert validate_record(record, 0) == []

    def test_excluded(self):
        record = _valid_record(status="excluded")
        assert validate_record(record, 0) == []

    def test_all_evidence_types(self):
        for etype in ("url", "repo-path", "self-reported", "inferred", "none"):
            record = _valid_record(evidence_type=etype)
            assert validate_record(record, 0) == [], f"Failed for type: {etype}"

    def test_all_sensitivities(self):
        for sens in ("public", "internal"):
            record = _valid_record(sensitivity=sens)
            assert validate_record(record, 0) == [], f"Failed for sensitivity: {sens}"

    def test_optional_repo_path(self):
        record = _valid_record(evidence_type="repo-path", repo_path="some/path.yml")
        record.pop("url", None)
        assert validate_record(record, 0) == []

    def test_optional_notes(self):
        record = _valid_record(notes="Some safe wording note.")
        assert validate_record(record, 0) == []


# ---------------------------------------------------------------------------
# validate_record — unresolved claims
# ---------------------------------------------------------------------------


class TestValidateRecordUnresolved:
    def test_needs_user_verification_is_not_an_error(self):
        """needs-user-verification records must be flagged but not rejected."""
        record = _valid_record(status="needs-user-verification", url=None)
        record.pop("url", None)
        errors = validate_record(record, 0)
        assert errors == []


# ---------------------------------------------------------------------------
# validate_record — excluded records
# ---------------------------------------------------------------------------


class TestValidateRecordExcluded:
    def test_excluded_is_not_an_error(self):
        record = _valid_record(status="excluded")
        record.pop("url", None)
        assert validate_record(record, 0) == []

    def test_sensitive_with_url_is_error(self):
        record = _valid_record(sensitivity="sensitive", url="https://private.example.com")
        errors = validate_record(record, 0)
        assert any("sensitive record must not have a 'url'" in e for e in errors)


# ---------------------------------------------------------------------------
# validate_record — malformed records
# ---------------------------------------------------------------------------


class TestValidateRecordMalformed:
    def test_not_a_dict(self):
        errors = validate_record("not a dict", 0)
        assert any("expected a mapping" in e for e in errors)

    def test_missing_required_field(self):
        record = _valid_record()
        del record["id"]
        errors = validate_record(record, 0)
        assert any("'id'" in e for e in errors)

    def test_unknown_field_rejected(self):
        record = _valid_record(unknown_field="bad")
        errors = validate_record(record, 0)
        assert any("unknown field" in e for e in errors)

    def test_invalid_status(self):
        record = _valid_record(status="published")
        errors = validate_record(record, 0)
        assert any("invalid status" in e for e in errors)

    def test_invalid_sensitivity(self):
        record = _valid_record(sensitivity="classified")
        errors = validate_record(record, 0)
        assert any("invalid sensitivity" in e for e in errors)

    def test_invalid_evidence_type(self):
        record = _valid_record(evidence_type="magic")
        errors = validate_record(record, 0)
        assert any("invalid evidence_type" in e for e in errors)

    def test_empty_claim(self):
        record = _valid_record(claim="   ")
        errors = validate_record(record, 0)
        assert any("'claim'" in e for e in errors)

    def test_empty_id(self):
        record = _valid_record(id="")
        errors = validate_record(record, 0)
        assert any("'id'" in e for e in errors)


# ---------------------------------------------------------------------------
# validate_file — integration tests
# ---------------------------------------------------------------------------


class TestValidateFile:
    def test_valid_catalog_passes(self, tmp_path):
        p = _write_catalog(tmp_path, [_valid_record()])
        assert validate_file(p) == 0

    def test_missing_file_returns_error(self, tmp_path):
        missing = tmp_path / "nonexistent.yml"
        assert validate_file(missing) == 1

    def test_empty_records_list_passes(self, tmp_path):
        p = _write_catalog(tmp_path, [])
        assert validate_file(p) == 0

    def test_malformed_record_in_file_fails(self, tmp_path):
        p = _write_catalog(tmp_path, [_valid_record(status="bad-status")])
        assert validate_file(p) == 1

    def test_duplicate_ids_fail(self, tmp_path):
        r1 = _valid_record(id="dup")
        r2 = _valid_record(id="dup")
        p = _write_catalog(tmp_path, [r1, r2])
        assert validate_file(p) == 1

    def test_unresolved_records_do_not_fail(self, tmp_path):
        record = _valid_record(status="needs-user-verification")
        record.pop("url", None)
        p = _write_catalog(tmp_path, [record])
        assert validate_file(p) == 0

    def test_excluded_records_do_not_fail(self, tmp_path):
        record = _valid_record(status="excluded")
        record.pop("url", None)
        p = _write_catalog(tmp_path, [record])
        assert validate_file(p) == 0

    def test_sensitive_with_url_fails(self, tmp_path):
        record = _valid_record(sensitivity="sensitive", url="https://private.example.com")
        p = _write_catalog(tmp_path, [record])
        assert validate_file(p) == 1

    def test_invalid_yaml_fails(self, tmp_path):
        bad = tmp_path / "evidence.yml"
        bad.write_text(": invalid: yaml: [[\n", encoding="utf-8")
        assert validate_file(bad) == 1

    def test_top_level_not_mapping_fails(self, tmp_path):
        bad = tmp_path / "evidence.yml"
        bad.write_text("- item1\n- item2\n", encoding="utf-8")
        assert validate_file(bad) == 1

    def test_missing_records_key_fails(self, tmp_path):
        bad = tmp_path / "evidence.yml"
        bad.write_text("schema_version: '1'\n", encoding="utf-8")
        assert validate_file(bad) == 1

    def test_production_catalog_passes(self):
        """The production evidence.yml must pass validation without errors."""
        prod = Path(__file__).parents[1] / "profile" / "content" / "evidence.yml"
        assert validate_file(prod) == 0
