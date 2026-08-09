#!/usr/bin/env python3
"""
Data quality checking module for monitoring and validation.

This module provides utilities to validate data quality including:
- Detection of missing required fields
- Detection of NaN/null values
- Validation of value ranges
- Logging of data quality warnings
"""

import json
import logging
import math
import sys
from typing import Any, Dict, List, Optional, Union


# Configure module logger
_quality_logger: Optional[logging.Logger] = None


def _get_quality_logger() -> logging.Logger:
    """Get or create the data quality logger."""
    global _quality_logger
    if _quality_logger is None:
        _quality_logger = logging.getLogger("data_quality")
        _quality_logger.setLevel(logging.WARNING)
        # Add console handler if none exists
        if not _quality_logger.handlers:
            handler = logging.StreamHandler(sys.stderr)
            handler.setLevel(logging.WARNING)
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            _quality_logger.addHandler(handler)
    return _quality_logger


def is_nan_value(value: Any) -> bool:
    """
    Check if a value is NaN (Not a Number).
    
    Args:
        value: Value to check
    
    Returns:
        True if value is NaN, False otherwise
    """
    if value is None:
        return False
    
    # Check for float NaN
    if isinstance(value, float) and math.isnan(value):
        return True
    
    # Check for string representations of NaN
    if isinstance(value, str) and value.lower() in ['nan', 'null', 'none', '']:
        return True
    
    return False


def check_missing_fields(
    data: Dict,
    required_fields: List[str],
    context: str = "data"
) -> List[str]:
    """
    Check for missing required fields in data.
    
    Args:
        data: Dictionary to validate
        required_fields: List of required field names
        context: Context description for logging
    
    Returns:
        List of missing field names (empty if all present)
    """
    logger = _get_quality_logger()
    missing = []
    
    for field in required_fields:
        if field not in data:
            missing.append(field)
            logger.warning(
                "⚠️ DATA_QUALITY: Missing required field '%s' in %s",
                field, context
            )
    
    return missing


def check_nan_values(
    data: Dict,
    fields_to_check: Optional[List[str]] = None,
    context: str = "data"
) -> Dict[str, Any]:
    """
    Check for NaN values in specified fields.
    
    Args:
        data: Dictionary to validate
        fields_to_check: List of field names to check (None = check all)
        context: Context description for logging
    
    Returns:
        Dictionary mapping field names to their NaN values
    """
    logger = _get_quality_logger()
    nan_fields = {}
    
    fields = fields_to_check if fields_to_check else list(data.keys())
    
    for field in fields:
        if field in data:
            value = data[field]
            if is_nan_value(value):
                nan_fields[field] = value
                logger.warning(
                    "⚠️ DATA_QUALITY: NaN/null value detected in field '%s' in %s: %s",
                    field, context, value
                )
    
    return nan_fields


def check_value_range(
    value: Union[int, float],
    min_value: Optional[Union[int, float]] = None,
    max_value: Optional[Union[int, float]] = None,
    field_name: str = "value",
    context: str = "data"
) -> bool:
    """
    Check if a numeric value is within expected range.
    
    Args:
        value: Numeric value to check
        min_value: Minimum acceptable value (None = no minimum)
        max_value: Maximum acceptable value (None = no maximum)
        field_name: Name of the field for logging
        context: Context description for logging
    
    Returns:
        True if value is in range, False otherwise
    """
    logger = _get_quality_logger()
    
    # Check for NaN first
    if is_nan_value(value):
        logger.warning(
            "⚠️ DATA_QUALITY: NaN value in field '%s' in %s",
            field_name, context
        )
        return False
    
    # Check minimum
    if min_value is not None and value < min_value:
        logger.warning(
            "⚠️ DATA_QUALITY: Value %s in field '%s' is below minimum %s in %s",
            value, field_name, min_value, context
        )
        return False
    
    # Check maximum
    if max_value is not None and value > max_value:
        logger.warning(
            "⚠️ DATA_QUALITY: Value %s in field '%s' is above maximum %s in %s",
            value, field_name, max_value, context
        )
        return False
    
    return True


def validate_data_quality(
    data: Dict,
    required_fields: Optional[List[str]] = None,
    numeric_ranges: Optional[Dict[str, Dict[str, Union[int, float]]]] = None,
    context: str = "data"
) -> Dict[str, Any]:
    """
    Comprehensive data quality validation.
    
    Args:
        data: Dictionary to validate
        required_fields: List of required field names
        numeric_ranges: Dictionary mapping field names to range specs
                       e.g., {'score': {'min': 0, 'max': 100}}
        context: Context description for logging
    
    Returns:
        Dictionary with validation results:
        - missing_fields: List of missing required fields
        - nan_fields: Dictionary of fields with NaN values
        - out_of_range: Dictionary of fields with out-of-range values
        - is_valid: Boolean indicating if all checks passed
    """
    results = {
        "missing_fields": [],
        "nan_fields": {},
        "out_of_range": {},
        "is_valid": True
    }
    
    # Check required fields
    if required_fields:
        missing = check_missing_fields(data, required_fields, context)
        if missing:
            results["missing_fields"] = missing
            results["is_valid"] = False
    
    # Check for NaN values
    nan_fields = check_nan_values(data, context=context)
    if nan_fields:
        results["nan_fields"] = nan_fields
        results["is_valid"] = False
    
    # Check numeric ranges
    if numeric_ranges:
        for field, range_spec in numeric_ranges.items():
            if field in data:
                value = data[field]
                if isinstance(value, (int, float)):
                    min_val = range_spec.get('min')
                    max_val = range_spec.get('max')
                    if not check_value_range(value, min_val, max_val, field, context):
                        results["out_of_range"][field] = {  # type: ignore[index]
                            "value": value,
                            "min": min_val,
                            "max": max_val
                        }
                        results["is_valid"] = False
    
    return results


def log_data_quality_summary(validation_results: Dict[str, Any], context: str = "data") -> None:
    """
    Log a summary of data quality validation results.
    
    Args:
        validation_results: Results from validate_data_quality()
        context: Context description for logging
    """
    logger = _get_quality_logger()
    
    if validation_results["is_valid"]:
        logger.info("✓ DATA_QUALITY: All checks passed for %s", context)
        return
    
    logger.warning("⚠️ DATA_QUALITY: Validation issues found in %s:", context)
    
    if validation_results["missing_fields"]:
        logger.warning(
            "  - Missing fields: %s",
            ", ".join(validation_results["missing_fields"])
        )
    
    if validation_results["nan_fields"]:
        logger.warning(
            "  - NaN/null fields: %s",
            ", ".join(validation_results["nan_fields"].keys())
        )
    
    if validation_results["out_of_range"]:
        for field, info in validation_results["out_of_range"].items():
            logger.warning(
                "  - Out of range: %s = %s (expected: [%s, %s])",
                field, info["value"], info["min"], info["max"]
            )
