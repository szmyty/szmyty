#!/usr/bin/env python3
"""
Tests for change detection module.
"""

import json
import subprocess
import tempfile
from pathlib import Path

import pytest

# Import the module to test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from lib.change_detection import (
    compute_file_hash,
    compute_json_hash,
    load_hash_cache,
    save_hash_cache,
    has_data_changed,
    update_hash_cache,
    should_regenerate_svg,
)


class TestComputeFileHash:
    """Test compute_file_hash function."""
    
    def test_hash_text_file(self):
        """Test hashing a text file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("Hello, World!")
            temp_path = Path(f.name)
        
        try:
            hash1 = compute_file_hash(temp_path)
            assert hash1 is not None
            assert len(hash1) == 64  # SHA256 produces 64 hex characters
            
            # Same content should produce same hash
            hash2 = compute_file_hash(temp_path)
            assert hash1 == hash2
        finally:
            temp_path.unlink()
    
    def test_hash_nonexistent_file(self):
        """Test hashing a nonexistent file returns None."""
        result = compute_file_hash(Path("/nonexistent/file.txt"))
        assert result is None
    
    def test_different_content_different_hash(self):
        """Test that different content produces different hashes."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f1:
            f1.write("Content A")
            path1 = Path(f1.name)
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f2:
            f2.write("Content B")
            path2 = Path(f2.name)
        
        try:
            hash1 = compute_file_hash(path1)
            hash2 = compute_file_hash(path2)
            assert hash1 != hash2
        finally:
            path1.unlink()
            path2.unlink()


class TestComputeJsonHash:
    """Test compute_json_hash function."""
    
    def test_hash_json_file(self):
        """Test hashing a JSON file."""
        data = {"key": "value", "number": 42}
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json.dump(data, f)
            temp_path = Path(f.name)
        
        try:
            hash_result = compute_json_hash(temp_path)
            assert hash_result is not None
            assert len(hash_result) == 64
        finally:
            temp_path.unlink()
    
    def test_json_formatting_doesnt_affect_hash(self):
        """Test that different JSON formatting produces the same hash."""
        data = {"b": 2, "a": 1}
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f1:
            json.dump(data, f1, indent=2)
            path1 = Path(f1.name)
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f2:
            json.dump(data, f2, indent=None)
            path2 = Path(f2.name)
        
        try:
            hash1 = compute_json_hash(path1)
            hash2 = compute_json_hash(path2)
            assert hash1 == hash2
        finally:
            path1.unlink()
            path2.unlink()
    
    def test_json_key_order_normalized(self):
        """Test that key order doesn't affect hash."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f1:
            f1.write('{"a": 1, "b": 2}')
            path1 = Path(f1.name)
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f2:
            f2.write('{"b": 2, "a": 1}')
            path2 = Path(f2.name)
        
        try:
            hash1 = compute_json_hash(path1)
            hash2 = compute_json_hash(path2)
            assert hash1 == hash2
        finally:
            path1.unlink()
            path2.unlink()
    
    def test_invalid_json_returns_none(self):
        """Test that invalid JSON returns None."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            f.write("not valid json{")
            temp_path = Path(f.name)
        
        try:
            result = compute_json_hash(temp_path)
            assert result is None
        finally:
            temp_path.unlink()


class TestHashCache:
    """Test hash cache operations."""
    
    def test_load_nonexistent_cache(self):
        """Test loading a nonexistent cache returns empty dict."""
        result = load_hash_cache(Path("/nonexistent/cache.json"))
        assert result == {}
    
    def test_save_and_load_cache(self):
        """Test saving and loading cache."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_path = Path(tmpdir) / "cache.json"
            cache_data = {"key1": "hash1", "key2": "hash2"}
            
            save_hash_cache(cache_path, cache_data)
            loaded = load_hash_cache(cache_path)
            
            assert loaded == cache_data
    
    def test_save_creates_directory(self):
        """Test that save_hash_cache creates parent directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_path = Path(tmpdir) / "subdir" / "cache.json"
            cache_data = {"key": "value"}
            
            save_hash_cache(cache_path, cache_data)
            assert cache_path.exists()
            
            loaded = load_hash_cache(cache_path)
            assert loaded == cache_data


class TestHasDataChanged:
    """Test has_data_changed function."""
    
    def test_new_file_is_changed(self):
        """Test that a new file is considered changed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            data_path = Path(tmpdir) / "data.json"
            cache_path = Path(tmpdir) / "cache.json"
            
            # Create data file
            with open(data_path, 'w') as f:
                json.dump({"key": "value"}, f)
            
            # No cache exists yet
            result = has_data_changed(data_path, cache_path, "test_key")
            assert result is True
    
    def test_unchanged_data_not_changed(self):
        """Test that unchanged data is not considered changed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            data_path = Path(tmpdir) / "data.json"
            cache_path = Path(tmpdir) / "cache.json"
            
            # Create data file
            with open(data_path, 'w') as f:
                json.dump({"key": "value"}, f)
            
            # Update cache
            update_hash_cache(data_path, cache_path, "test_key")
            
            # Should not be changed
            result = has_data_changed(data_path, cache_path, "test_key")
            assert result is False
    
    def test_modified_data_is_changed(self):
        """Test that modified data is considered changed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            data_path = Path(tmpdir) / "data.json"
            cache_path = Path(tmpdir) / "cache.json"
            
            # Create and cache original data
            with open(data_path, 'w') as f:
                json.dump({"key": "value1"}, f)
            update_hash_cache(data_path, cache_path, "test_key")
            
            # Modify data
            with open(data_path, 'w') as f:
                json.dump({"key": "value2"}, f)
            
            # Should be changed
            result = has_data_changed(data_path, cache_path, "test_key")
            assert result is True


class TestShouldRegenerateSvg:
    """Test should_regenerate_svg function."""
    
    def test_force_regenerate(self):
        """Test that force=True always regenerates."""
        with tempfile.TemporaryDirectory() as tmpdir:
            data_path = Path(tmpdir) / "data.json"
            svg_path = Path(tmpdir) / "output.svg"
            cache_path = Path(tmpdir) / "cache.json"
            
            # Create files
            with open(data_path, 'w') as f:
                json.dump({"key": "value"}, f)
            with open(svg_path, 'w') as f:
                f.write("<svg></svg>")
            
            # Cache the data
            update_hash_cache(data_path, cache_path, "test")
            
            # Force should regenerate even though data unchanged
            result = should_regenerate_svg(data_path, svg_path, cache_path, "test", force=True)
            assert result is True
    
    def test_missing_svg_regenerates(self):
        """Test that missing SVG triggers regeneration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            data_path = Path(tmpdir) / "data.json"
            svg_path = Path(tmpdir) / "output.svg"
            cache_path = Path(tmpdir) / "cache.json"
            
            # Create only data file
            with open(data_path, 'w') as f:
                json.dump({"key": "value"}, f)
            
            result = should_regenerate_svg(data_path, svg_path, cache_path, "test")
            assert result is True
    
    def test_unchanged_data_skips_regeneration(self):
        """Test that unchanged data skips regeneration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            data_path = Path(tmpdir) / "data.json"
            svg_path = Path(tmpdir) / "output.svg"
            cache_path = Path(tmpdir) / "cache.json"
            
            # Create files
            with open(data_path, 'w') as f:
                json.dump({"key": "value"}, f)
            with open(svg_path, 'w') as f:
                f.write("<svg></svg>")
            
            # Cache the data
            update_hash_cache(data_path, cache_path, "test")
            
            # Should skip regeneration
            result = should_regenerate_svg(data_path, svg_path, cache_path, "test")
            assert result is False


class TestIncrementalGenerate:
    """Test incremental-generate.py wrapper functionality."""
    
    def test_generator_path_validation(self):
        """Test that generator script path is validated for security."""
        # Test the validation logic by calling the wrapper as subprocess
        import subprocess
        
        with tempfile.TemporaryDirectory() as tmpdir:
            data_path = Path(tmpdir) / "data.json"
            svg_path = Path(tmpdir) / "output.svg"
            
            # Create data file
            with open(data_path, 'w') as f:
                json.dump({"key": "value"}, f)
            
            # Get path to incremental-generate.py
            script_path = Path(__file__).parent.parent / "scripts" / "incremental-generate.py"
            
            # Try to use a script outside scripts/ directory
            result = subprocess.run(
                ["python", str(script_path), str(data_path), str(svg_path), "/etc/passwd", "test"],
                capture_output=True,
                text=True
            )
            
            # Should fail with error message about generator script
            assert result.returncode != 0
            assert "Generator script must be in scripts/ directory" in result.stdout or "Generator script must be in scripts/ directory" in result.stderr
