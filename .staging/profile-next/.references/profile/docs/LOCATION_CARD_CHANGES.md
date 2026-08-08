# Location Card Fail-Safe and Diagnostic Changes

## Summary

This document summarizes the changes made to add comprehensive failure detection and diagnostic output to the location map card generation workflow.

## Problem Statement

The location map card was not rendering, and failures were happening silently without actionable error messages. Users had no way to diagnose issues related to:
- API rate limiting
- Invalid responses
- Network failures
- Missing or corrupted data

## Solution

Added comprehensive diagnostics and fail-safes throughout the location card generation pipeline to ensure failures are never silent and always provide actionable guidance.

## Changes Made

### 1. Enhanced Shell Scripts (`scripts/fetch-location.sh` and `scripts/lib/common.sh`)

#### Nominatim API Error Detection
- Capture HTTP status codes and curl exit codes
- Detect rate limiting (HTTP 429) with specific guidance
- Identify invalid JSON responses
- Check for empty responses
- Save diagnostic data to `location/debug_nominatim.json` and `location/debug_nominatim_response.txt`

**Example Error Messages:**
```bash
❌ FAILURE: Nominatim API returned error (HTTP Code: 429)
   → Rate limiting detected
   → Nominatim has strict rate limits (1 request per second)
   → Wait at least 1 hour before retrying or use caching
   → Consider using a commercial geocoding service for production
```

#### Static Map Download Error Detection
- Capture HTTP status codes for map downloads
- Detect authentication failures (401/403)
- Identify rate limiting (429)
- Check for service errors (500+)
- Save diagnostic data to `location/debug_map_response.txt`

**Example Error Messages:**
```bash
❌ FAILURE: Map retrieval failed (HTTP Code: 403)
   → Authentication required or access forbidden
   → Map service may require API key or token
   → Check if the service has changed its authentication requirements
```

### 2. Enhanced Python Script (`scripts/generate-location-card.py`)

#### Metadata Validation
- Check if metadata file exists
- Validate JSON structure
- Verify required fields (location, coordinates)
- Provide specific error messages for each failure

**Example Error Messages:**
```python
❌ FAILURE: Missing 'location' field in metadata
   → The metadata file is missing required fields
```

#### Map Image Processing
- Validate map file exists
- Check file is readable
- Verify image encoding produces valid base64
- Check minimum base64 length (prevents empty/corrupted images)
- Validate SVG contains embedded image

**Example Error Messages:**
```python
❌ FAILURE: Map image not found: location/location-map.png
   → The map download may have failed
   → Check debug_map_response.txt in the location directory
```

#### SVG Generation Validation
- Verify SVG starts with `<svg` tag
- Check that map image is embedded in SVG
- Validate final SVG before writing
- Report diagnostic info on success (size, base64 length)

**Success Messages:**
```python
✅ Generated location SVG card: location/location-card.svg
   → Card size: 2367 characters
   → Base64 image size: 148 characters
```

### 3. Diagnostic Files

Three diagnostic files are now created to aid in troubleshooting:

1. **`location/debug_nominatim.json`**
   - Raw JSON response from Nominatim API
   - Helps identify response structure issues

2. **`location/debug_nominatim_response.txt`**
   - Complete request/response details
   - Includes URL, HTTP code, curl exit code, headers
   - Contains full response body

3. **`location/debug_map_response.txt`**
   - Map download request/response details
   - Includes HTTP code, curl exit code, headers
   - Shows file size of downloaded image

**Privacy Note:** These files contain location data and are automatically excluded from git commits via `.gitignore`.

### 4. Test Coverage

#### Python Tests (`tests/test_location_diagnostics.py`)
- Tests for missing metadata file
- Tests for invalid JSON
- Tests for missing required fields
- Tests for missing map file
- Tests for empty map file
- Tests for successful generation with diagnostics
- Tests for utility functions

10 new tests added, all passing.

#### Shell Script Tests (`tests/test_location_shell_diagnostics.sh`)
- Tests diagnostic file creation on failure
- Tests diagnostic content correctness
- Tests error message formatting
- Tests get_coordinates function

8 new tests added, all passing.

#### End-to-End Test
Complete workflow validation from metadata to SVG card generation.

### 5. Documentation

#### `docs/LOCATION_DIAGNOSTICS.md`
Comprehensive troubleshooting guide including:
- Overview of the location card generation process
- Description of diagnostic files
- Common failure scenarios with solutions
- Error message format guide
- Workflow integration details
- Testing instructions
- Best practices
- Troubleshooting checklist

### 6. Updated `.gitignore`
Added patterns to exclude diagnostic files from git commits:
```gitignore
# Location debug files (saved for debugging but not committed)
location/debug_*.json
location/debug_*.txt

# API response cache
cached/
```

## Error Message Format

All error messages follow a consistent, actionable format:

```
❌ FAILURE: <Brief description>
   → <Specific cause or symptom>
   → <Actionable resolution step>
   → <Additional context or documentation link>
```

Success messages:
```
✅ <What succeeded>
   → <Diagnostic information>
```

## Testing Results

All tests pass successfully:
- **172 total tests pass** (162 existing + 10 new)
- **8 shell script tests pass**
- **End-to-end integration test passes**
- **No security vulnerabilities detected** (CodeQL scan: 0 alerts)

## Benefits

1. **Never Silent Failures**: Every failure produces clear diagnostic output
2. **Actionable Guidance**: Error messages tell users exactly what to do
3. **Debug-Friendly**: Diagnostic files provide all information needed to troubleshoot
4. **Rate Limit Aware**: Specific detection and guidance for API rate limiting
5. **Comprehensive Coverage**: All failure points have error detection
6. **Well-Tested**: Extensive test coverage ensures reliability
7. **Well-Documented**: Complete troubleshooting guide for users

## Code Review Feedback Addressed

1. ✅ Fixed trap cleanup in shell tests to prevent temp directory leaks
2. ✅ Added privacy note about location data in diagnostic files
3. ✅ Documented magic number (MIN_BASE64_LENGTH = 100) with explanation
4. ✅ Added note about diagnostic file sensitivity in shell script

## Files Changed

- `scripts/fetch-location.sh`: +78 lines
- `scripts/lib/common.sh`: +97 lines
- `scripts/generate-location-card.py`: +104 lines
- `.gitignore`: +5 lines
- `tests/test_location_diagnostics.py`: +251 lines (new)
- `tests/test_location_shell_diagnostics.sh`: +145 lines (new)
- `docs/LOCATION_DIAGNOSTICS.md`: +256 lines (new)
- `docs/LOCATION_CARD_CHANGES.md`: This file (new)

**Total**: 936 lines added, 30 lines modified

## Future Improvements

Potential enhancements for future consideration:

1. Add support for alternative geocoding services (Google, Mapbox)
2. Implement automatic retry with exponential backoff for transient failures
3. Add metrics/monitoring for failure rates
4. Create a dashboard showing diagnostic status
5. Add email/notification alerts for repeated failures

## Conclusion

The location card generation workflow now has comprehensive fail-safes and diagnostic capabilities that make it easy to identify and resolve issues. All failures produce actionable error messages, and diagnostic files provide complete information for troubleshooting.
