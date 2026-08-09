#!/bin/bash
# Helper script to test GitHub Actions locally with act
# Usage: ./scripts/act-test.sh [workflow-name] [job-name]

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if act is installed
if ! command -v act &> /dev/null; then
    echo -e "${RED}Error: act is not installed${NC}"
    echo "Install it with: curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash"
    exit 1
fi

# Check if Docker is running
if ! docker ps &> /dev/null; then
    echo -e "${RED}Error: Docker is not running${NC}"
    echo "Please start Docker and try again"
    exit 1
fi

# Function to display usage
usage() {
    echo -e "${GREEN}GitHub Actions Local Testing with act${NC}"
    echo ""
    echo "Usage: $0 [workflow-name] [job-name]"
    echo ""
    echo "Examples:"
    echo "  $0                    # List all workflows and jobs"
    echo "  $0 tests              # Run all jobs in tests.yml"
    echo "  $0 tests test-python  # Run specific job in tests.yml"
    echo ""
    echo "Available workflows:"
    echo "  - act-demo           (.github/workflows/act-demo.yml) ✨ Recommended for testing"
    echo "  - tests              (.github/workflows/tests.yml)"
    echo "  - build-profile      (.github/workflows/build-profile.yml)"
    echo "  - monitoring         (.github/workflows/monitoring.yml)"
    echo "  - release            (.github/workflows/release.yml)"
    echo "  - greetings          (.github/workflows/greetings.yml)"
    echo ""
    echo "Note: Some workflows use composite actions and may not work with act."
    echo "See .github/workflows/ACT_LIMITATIONS.md for details."
    echo ""
    echo "Tip: Check .secrets file for required tokens"
}

# Function to list all workflows
list_workflows() {
    echo -e "${GREEN}Available workflows and jobs:${NC}"
    echo ""
    act -l
}

# Function to run a specific workflow
run_workflow() {
    local workflow=$1
    local job=$2
    local workflow_file=".github/workflows/${workflow}.yml"
    
    if [ ! -f "$workflow_file" ]; then
        echo -e "${RED}Error: Workflow file not found: ${workflow_file}${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}Running workflow: ${workflow}${NC}"
    
    # Check for secrets file
    if [ -f ".secrets" ]; then
        echo -e "${YELLOW}Using secrets from .secrets file${NC}"
        SECRET_FLAG="--secret-file .secrets"
    else
        echo -e "${YELLOW}Warning: .secrets file not found${NC}"
        echo "Copy .secrets.example to .secrets and add your tokens"
        SECRET_FLAG=""
    fi
    
    if [ -n "$job" ]; then
        echo -e "${GREEN}Running job: ${job}${NC}"
        # shellcheck disable=SC2086
        act -W "$workflow_file" -j "$job" $SECRET_FLAG
    else
        echo -e "${GREEN}Running all jobs in workflow${NC}"
        # shellcheck disable=SC2086
        act -W "$workflow_file" $SECRET_FLAG
    fi
}

# Main script logic
case "$1" in
    -h|--help|help)
        usage
        ;;
    "")
        list_workflows
        ;;
    *)
        run_workflow "$1" "$2"
        ;;
esac
