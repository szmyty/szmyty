"""Deterministic file-hashing for AI-invalidation logic.

Metadata boundary
-----------------
Only **deterministic** inputs are ever passed to hashing functions:

- Binary file contents (e.g. ``page.png``) via :func:`hash_file`.
- Structured config dicts (serialised with ``json.dumps(sort_keys=True)``).

Timestamps, run-time environment details, and other non-deterministic data
must **never** influence hash values so that invalidation logic remains
stable across builds.
"""

import hashlib
from pathlib import Path


def hash_file(path: Path | str, algorithm: str = "sha256") -> str:
    """Return the hex digest of *path* using *algorithm*.

    Reads the file in chunks to handle large images without loading the entire
    file into memory.
    """
    h = hashlib.new(algorithm)
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()
