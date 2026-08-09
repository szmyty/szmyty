#!/usr/bin/env python3
"""
Change detection utilities for incremental SVG regeneration.
This module provides hash-based change detection to skip SVG regeneration
when the source data hasn't changed.
"""

import hashlib
import json
import sys
from pathlib import Path
from typing import Optional


def compute_file_hash(file_path: Path) -> Optional[str]:
    """
    Compute SHA256 hash of a file's contents.
    
    Args:
        file_path: Path to the file to hash
        
    Returns:
        Hexadecimal string representation of the hash, or None if file doesn't exist
    """
    if not file_path.exists():
        return None
    
    try:
        with open(file_path, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()
    except (IOError, OSError):
        return None


def compute_json_hash(json_path: Path) -> Optional[str]:
    """
    Compute SHA256 hash of normalized JSON data.
    This ensures consistent hashing regardless of formatting changes.
    
    Args:
        json_path: Path to the JSON file to hash
        
    Returns:
        Hexadecimal string representation of the hash, or None if file doesn't exist or is invalid
    """
    if not json_path.exists():
        return None
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Normalize JSON by sorting keys and using compact representation
        normalized = json.dumps(data, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(normalized.encode('utf-8')).hexdigest()
    except (IOError, OSError, json.JSONDecodeError):
        return None


def load_hash_cache(cache_path: Path) -> dict:
    """
    Load hash cache from JSON file.
    
    Args:
        cache_path: Path to the cache file
        
    Returns:
        Dictionary with cached hashes, empty dict if file doesn't exist or is invalid
    """
    if not cache_path.exists():
        return {}
    
    try:
        with open(cache_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (IOError, OSError, json.JSONDecodeError):
        return {}


def save_hash_cache(cache_path: Path, cache_data: dict) -> None:
    """
    Save hash cache to JSON file using safe write pattern.
    
    Args:
        cache_path: Path to the cache file
        cache_data: Dictionary with hashes to save
    """
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = cache_path.parent / f"{cache_path.name}.tmp"
    
    try:
        # Write to temporary file
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, indent=2)
        
        # Validate the temp file can be loaded
        with open(temp_path, 'r', encoding='utf-8') as f:
            json.load(f)
        
        # Atomic move to final location
        temp_path.replace(cache_path)
        
    except (IOError, OSError, json.JSONDecodeError) as e:
        # Clean up temp file on failure (missing_ok=True available in Python 3.8+)
        temp_path.unlink(missing_ok=True)
        # Log cache write failure but don't fail the operation
        print(f"Warning: Could not save hash cache to {cache_path}: {e}", file=sys.stderr)


def has_data_changed(
    data_path: Path,
    cache_path: Path,
    cache_key: str
) -> bool:
    """
    Check if data file has changed since last generation.
    
    Args:
        data_path: Path to the data file (JSON or other)
        cache_path: Path to the hash cache file
        cache_key: Key to use in the cache (e.g., 'oura_metrics')
        
    Returns:
        True if data has changed or is new, False if unchanged
    """
    # Compute current hash
    if data_path.suffix == '.json':
        current_hash = compute_json_hash(data_path)
    else:
        current_hash = compute_file_hash(data_path)
    
    if current_hash is None:
        return True  # File doesn't exist, consider it changed
    
    # Load cache
    cache = load_hash_cache(cache_path)
    
    # Check if hash changed
    cached_hash = cache.get(cache_key)
    return cached_hash != current_hash


def update_hash_cache(
    data_path: Path,
    cache_path: Path,
    cache_key: str
) -> None:
    """
    Update hash cache with current data file hash.
    
    Args:
        data_path: Path to the data file
        cache_path: Path to the hash cache file
        cache_key: Key to use in the cache
    """
    # Compute current hash
    if data_path.suffix == '.json':
        current_hash = compute_json_hash(data_path)
    else:
        current_hash = compute_file_hash(data_path)
    
    if current_hash is None:
        return  # Can't compute hash, don't update cache
    
    # Load existing cache
    cache = load_hash_cache(cache_path)
    
    # Update cache
    cache[cache_key] = current_hash
    
    # Save cache
    save_hash_cache(cache_path, cache)


def should_regenerate_svg(
    data_path: Path,
    svg_path: Path,
    cache_path: Path,
    cache_key: str,
    force: bool = False
) -> bool:
    """
    Determine if SVG should be regenerated based on data changes.
    
    Args:
        data_path: Path to the source data file
        svg_path: Path to the SVG output file
        cache_path: Path to the hash cache file
        cache_key: Key to use in the cache
        force: If True, always regenerate (default: False)
        
    Returns:
        True if SVG should be regenerated, False to skip
    """
    # Always regenerate if forced
    if force:
        return True
    
    # Regenerate if SVG doesn't exist
    if not svg_path.exists():
        return True
    
    # Regenerate if data file doesn't exist
    if not data_path.exists():
        return True
    
    # Check if data has changed
    return has_data_changed(data_path, cache_path, cache_key)
