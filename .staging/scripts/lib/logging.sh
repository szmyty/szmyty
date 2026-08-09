#!/bin/bash
# Logging utilities for profile scripts.
# Provides centralized logging functionality with rotation support.

# Default log configuration
LOG_DIR="${LOG_DIR:-logs}"
LOG_MAX_SIZE="${LOG_MAX_SIZE:-5242880}"  # 5MB in bytes
LOG_MAX_ROTATIONS="${LOG_MAX_ROTATIONS:-3}"

# Get the current workflow name from the environment or fallback
get_workflow_name() {
    # Try to extract workflow name from GITHUB_WORKFLOW env var
    if [ -n "${GITHUB_WORKFLOW:-}" ]; then
        # Convert workflow name to lowercase, replace spaces with hyphens
        echo "$GITHUB_WORKFLOW" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | sed 's/[^a-z0-9-]//g'
    else
        echo "unknown"
    fi
}

# Initialize logging for a specific workflow
# Usage: init_logging "location"
init_logging() {
    local workflow_name="${1:-$(get_workflow_name)}"
    
    # Create log directory if it doesn't exist
    mkdir -p "${LOG_DIR}/${workflow_name}"
    
    # Set the log file path as a global variable
    export LOG_FILE="${LOG_DIR}/${workflow_name}/${workflow_name}.log"
    
    echo "Logging initialized: ${LOG_FILE}" >&2
}

# Rotate log file if it exceeds maximum size
# Usage: rotate_log_if_needed
rotate_log_if_needed() {
    if [ -z "${LOG_FILE:-}" ]; then
        echo "Warning: LOG_FILE not set, skipping rotation" >&2
        return 0
    fi
    
    # Check if log file exists and its size
    if [ ! -f "$LOG_FILE" ]; then
        return 0
    fi
    
    local file_size
    if stat -c %s "$LOG_FILE" > /dev/null 2>&1; then
        # Linux
        file_size=$(stat -c %s "$LOG_FILE")
    elif stat -f %z "$LOG_FILE" > /dev/null 2>&1; then
        # macOS/BSD
        file_size=$(stat -f %z "$LOG_FILE")
    else
        echo "Warning: Cannot determine log file size" >&2
        return 0
    fi
    
    # Check if rotation is needed
    if [ "$file_size" -lt "$LOG_MAX_SIZE" ]; then
        return 0
    fi
    
    echo "Log rotation triggered (size: ${file_size} bytes, max: ${LOG_MAX_SIZE} bytes)" >&2
    
    # Rotate existing log files
    for i in $(seq $((LOG_MAX_ROTATIONS)) -1 1); do
        local current="${LOG_FILE}.${i}"
        local next="${LOG_FILE}.$((i + 1))"
        
        if [ -f "$current" ]; then
            if [ "$i" -eq $((LOG_MAX_ROTATIONS)) ]; then
                # Delete the oldest log
                rm -f "$current"
                echo "Deleted oldest log: $current" >&2
            else
                # Rotate the log
                mv "$current" "$next"
                echo "Rotated: $current -> $next" >&2
            fi
        fi
    done
    
    # Rotate current log to .1
    mv "$LOG_FILE" "${LOG_FILE}.1"
    echo "Rotated: $LOG_FILE -> ${LOG_FILE}.1" >&2
    
    # Create new empty log file
    touch "$LOG_FILE"
}

# Log a message with timestamp and severity
# Usage: log "INFO" "Message to log"
# Usage: log "ERROR" "Error message"
log() {
    local severity="${1:-INFO}"
    local message="${2:-}"
    local timestamp
    timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    
    # Format: [TIMESTAMP] [SEVERITY] Message
    local log_entry="[${timestamp}] [${severity}] ${message}"
    
    # Output to stderr for console visibility
    echo "$log_entry" >&2
    
    # Append to log file if initialized
    if [ -n "${LOG_FILE:-}" ]; then
        echo "$log_entry" >> "$LOG_FILE"
    fi
}

# Convenience functions for different log levels
log_info() {
    log "INFO" "$1"
}

log_warn() {
    log "WARN" "$1"
}

log_error() {
    log "ERROR" "$1"
}

# Log command execution with return code
# Usage: log_command "curl -sf https://api.example.com"
log_command() {
    local cmd="$1"
    local timestamp
    timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    
    log_info "Executing: ${cmd}"
    
    # Execute command and capture output and exit code
    local output
    local exit_code
    
    output=$($cmd 2>&1)
    exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        log_info "Command succeeded (exit code: ${exit_code})"
        echo "$output"
        return 0
    else
        log_error "Command failed (exit code: ${exit_code})"
        log_error "Output: ${output}"
        return $exit_code
    fi
}

# Log workflow start
# Usage: log_workflow_start "Location Card Update"
log_workflow_start() {
    local workflow_name="${1:-Unknown Workflow}"
    local separator="============================================================"
    
    log_info "$separator"
    log_info "Workflow: ${workflow_name}"
    log_info "Started at: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
    log_info "$separator"
}

# Log workflow end
# Usage: log_workflow_end "Location Card Update" 0
log_workflow_end() {
    local workflow_name="${1:-Unknown Workflow}"
    local exit_code="${2:-0}"
    local separator="============================================================"
    
    log_info "$separator"
    if [ "$exit_code" -eq 0 ]; then
        log_info "Workflow: ${workflow_name} - COMPLETED SUCCESSFULLY"
    else
        log_error "Workflow: ${workflow_name} - FAILED (exit code: ${exit_code})"
    fi
    log_info "Ended at: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
    log_info "$separator"
    
    # Check if log rotation is needed at end of workflow
    rotate_log_if_needed
}

# Export functions for use in scripts
export -f init_logging
export -f rotate_log_if_needed
export -f log
export -f log_info
export -f log_warn
export -f log_error
export -f log_command
export -f log_workflow_start
export -f log_workflow_end
export -f get_workflow_name
