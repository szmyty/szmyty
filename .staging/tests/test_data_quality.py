#!/usr/bin/env python3
"""
Unit tests for scripts/lib/data_quality.py
"""

import pytest
import sys
import os
import math

# Add scripts directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from lib.data_quality import (
    is_nan_value,
    check_missing_fields,
    check_nan_values,
    check_value_range,
    validate_data_quality,
)


class TestIsNanValue:
    """Tests for is_nan_value function."""
    
    def test_none_is_not_nan(self):
        """None is not considered NaN."""
        assert is_nan_value(None) is False
    
    def test_float_nan_detected(self):
        """Float NaN is detected."""
        assert is_nan_value(float('nan')) is True
        assert is_nan_value(math.nan) is True
    
    def test_string_nan_detected(self):
        """String representations of NaN are detected."""
        assert is_nan_value('nan') is True
        assert is_nan_value('NaN') is True
        assert is_nan_value('NAN') is True
        assert is_nan_value('null') is True
        assert is_nan_value('none') is True
        assert is_nan_value('') is True
    
    def test_valid_values_not_nan(self):
        """Valid values are not detected as NaN."""
        assert is_nan_value(0) is False
        assert is_nan_value(42) is False
        assert is_nan_value(3.14) is False
        assert is_nan_value('hello') is False
        assert is_nan_value([1, 2, 3]) is False


class TestCheckMissingFields:
    """Tests for check_missing_fields function."""
    
    def test_no_missing_fields(self):
        """Returns empty list when all fields present."""
        data = {"name": "test", "value": 42, "status": "ok"}
        required = ["name", "value", "status"]
        
        missing = check_missing_fields(data, required)
        assert missing == []
    
    def test_some_missing_fields(self):
        """Returns list of missing fields."""
        data = {"name": "test"}
        required = ["name", "value", "status"]
        
        missing = check_missing_fields(data, required)
        assert set(missing) == {"value", "status"}
    
    def test_all_fields_missing(self):
        """Returns all fields when none present."""
        data = {}
        required = ["name", "value", "status"]
        
        missing = check_missing_fields(data, required)
        assert set(missing) == {"name", "value", "status"}
    
    def test_empty_required_list(self):
        """Returns empty list when no fields required."""
        data = {"name": "test"}
        required = []
        
        missing = check_missing_fields(data, required)
        assert missing == []


class TestCheckNanValues:
    """Tests for check_nan_values function."""
    
    def test_no_nan_values(self):
        """Returns empty dict when no NaN values."""
        data = {"name": "test", "value": 42, "score": 85.5}
        
        nan_fields = check_nan_values(data)
        assert nan_fields == {}
    
    def test_float_nan_detected(self):
        """Detects float NaN values."""
        data = {"name": "test", "value": float('nan'), "score": 85.5}
        
        nan_fields = check_nan_values(data)
        assert "value" in nan_fields
        assert math.isnan(nan_fields["value"])
    
    def test_string_nan_detected(self):
        """Detects string NaN values."""
        data = {"name": "test", "value": "nan", "score": "null"}
        
        nan_fields = check_nan_values(data)
        assert "value" in nan_fields
        assert "score" in nan_fields
    
    def test_specific_fields_checked(self):
        """Only checks specified fields."""
        data = {"name": "nan", "value": "nan", "score": 85.5}
        
        nan_fields = check_nan_values(data, fields_to_check=["value"])
        assert "value" in nan_fields
        assert "name" not in nan_fields


class TestCheckValueRange:
    """Tests for check_value_range function."""
    
    def test_value_in_range(self):
        """Returns True for value in range."""
        assert check_value_range(50, min_value=0, max_value=100) is True
        assert check_value_range(0, min_value=0, max_value=100) is True
        assert check_value_range(100, min_value=0, max_value=100) is True
    
    def test_value_below_minimum(self):
        """Returns False for value below minimum."""
        assert check_value_range(-1, min_value=0, max_value=100) is False
    
    def test_value_above_maximum(self):
        """Returns False for value above maximum."""
        assert check_value_range(101, min_value=0, max_value=100) is False
    
    def test_no_minimum_constraint(self):
        """Works without minimum constraint."""
        assert check_value_range(-1000, max_value=100) is True
        assert check_value_range(101, max_value=100) is False
    
    def test_no_maximum_constraint(self):
        """Works without maximum constraint."""
        assert check_value_range(1000, min_value=0) is True
        assert check_value_range(-1, min_value=0) is False
    
    def test_nan_value_returns_false(self):
        """Returns False for NaN values."""
        assert check_value_range(float('nan'), min_value=0, max_value=100) is False


class TestValidateDataQuality:
    """Tests for validate_data_quality function."""
    
    def test_all_checks_pass(self):
        """Returns valid result when all checks pass."""
        data = {"name": "test", "score": 85, "value": 42}
        required_fields = ["name", "score", "value"]
        numeric_ranges = {
            "score": {"min": 0, "max": 100},
            "value": {"min": 0, "max": 100}
        }
        
        result = validate_data_quality(
            data,
            required_fields=required_fields,
            numeric_ranges=numeric_ranges
        )
        
        assert result["is_valid"] is True
        assert result["missing_fields"] == []
        assert result["nan_fields"] == {}
        assert result["out_of_range"] == {}
    
    def test_missing_fields_detected(self):
        """Detects missing required fields."""
        data = {"name": "test"}
        required_fields = ["name", "score", "value"]
        
        result = validate_data_quality(data, required_fields=required_fields)
        
        assert result["is_valid"] is False
        assert set(result["missing_fields"]) == {"score", "value"}
    
    def test_nan_values_detected(self):
        """Detects NaN values."""
        data = {"name": "test", "score": float('nan'), "value": "null"}
        
        result = validate_data_quality(data)
        
        assert result["is_valid"] is False
        assert "score" in result["nan_fields"]
        assert "value" in result["nan_fields"]
    
    def test_out_of_range_detected(self):
        """Detects out-of-range values."""
        data = {"score": 150, "value": -10}
        numeric_ranges = {
            "score": {"min": 0, "max": 100},
            "value": {"min": 0, "max": 100}
        }
        
        result = validate_data_quality(
            data,
            numeric_ranges=numeric_ranges
        )
        
        assert result["is_valid"] is False
        assert "score" in result["out_of_range"]
        assert "value" in result["out_of_range"]
        assert result["out_of_range"]["score"]["value"] == 150
        assert result["out_of_range"]["value"]["value"] == -10
    
    def test_multiple_issues_detected(self):
        """Detects multiple types of issues simultaneously."""
        data = {"score": float('nan')}
        required_fields = ["score", "name", "value"]
        numeric_ranges = {"score": {"min": 0, "max": 100}}
        
        result = validate_data_quality(
            data,
            required_fields=required_fields,
            numeric_ranges=numeric_ranges
        )
        
        assert result["is_valid"] is False
        assert set(result["missing_fields"]) == {"name", "value"}
        assert "score" in result["nan_fields"]
    
    def test_no_validation_rules(self):
        """Works with no validation rules specified."""
        data = {"name": "test", "score": 85}
        
        result = validate_data_quality(data)
        
        # Should pass if no NaN values
        assert result["is_valid"] is True
