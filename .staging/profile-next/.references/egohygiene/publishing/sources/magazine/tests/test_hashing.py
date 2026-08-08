"""Tests for hashing logic (magazine.hashing)."""

import hashlib
from pathlib import Path

import pytest

from magazine.hashing import hash_file


class TestHashFile:
    def test_returns_hex_string(self, tmp_path: Path) -> None:
        f = tmp_path / "sample.bin"
        f.write_bytes(b"hello world")
        digest = hash_file(f)
        assert isinstance(digest, str)
        assert all(c in "0123456789abcdef" for c in digest)

    def test_sha256_length(self, tmp_path: Path) -> None:
        f = tmp_path / "sample.bin"
        f.write_bytes(b"hello world")
        assert len(hash_file(f)) == 64

    def test_deterministic(self, tmp_path: Path) -> None:
        f = tmp_path / "sample.bin"
        f.write_bytes(b"reproducible content")
        assert hash_file(f) == hash_file(f)

    def test_different_content_different_hash(self, tmp_path: Path) -> None:
        f1 = tmp_path / "a.bin"
        f2 = tmp_path / "b.bin"
        f1.write_bytes(b"content A")
        f2.write_bytes(b"content B")
        assert hash_file(f1) != hash_file(f2)

    def test_same_content_same_hash(self, tmp_path: Path) -> None:
        f1 = tmp_path / "x.bin"
        f2 = tmp_path / "y.bin"
        data = b"identical content"
        f1.write_bytes(data)
        f2.write_bytes(data)
        assert hash_file(f1) == hash_file(f2)

    def test_matches_stdlib_sha256(self, tmp_path: Path) -> None:
        data = b"test content for verification"
        f = tmp_path / "check.bin"
        f.write_bytes(data)
        expected = hashlib.sha256(data).hexdigest()
        assert hash_file(f) == expected

    def test_accepts_string_path(self, tmp_path: Path) -> None:
        f = tmp_path / "str_path.bin"
        f.write_bytes(b"data")
        assert hash_file(str(f)) == hash_file(f)

    def test_large_file_chunked_correctly(self, tmp_path: Path) -> None:
        """Files larger than one 64 KiB chunk are hashed correctly."""
        data = b"x" * (65536 * 3 + 1000)
        f = tmp_path / "large.bin"
        f.write_bytes(data)
        expected = hashlib.sha256(data).hexdigest()
        assert hash_file(f) == expected

    def test_hash_changes_when_file_changes(self, tmp_path: Path) -> None:
        f = tmp_path / "mutable.bin"
        f.write_bytes(b"original")
        h1 = hash_file(f)
        f.write_bytes(b"modified")
        h2 = hash_file(f)
        assert h1 != h2

    def test_hash_stable_when_file_unchanged(self, tmp_path: Path) -> None:
        f = tmp_path / "stable.bin"
        f.write_bytes(b"unchanging data")
        hashes = [hash_file(f) for _ in range(5)]
        assert len(set(hashes)) == 1

    def test_algorithm_md5(self, tmp_path: Path) -> None:
        f = tmp_path / "md5test.bin"
        f.write_bytes(b"md5 data")
        digest = hash_file(f, algorithm="md5")
        assert len(digest) == 32

    def test_empty_file(self, tmp_path: Path) -> None:
        f = tmp_path / "empty.bin"
        f.write_bytes(b"")
        digest = hash_file(f)
        assert digest == hashlib.sha256(b"").hexdigest()
