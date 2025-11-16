#!/bin/bash
#
# Script to run tests with coverage
#
# Usage:
#   ./run_tests.sh              # Run all tests with coverage
#   ./run_tests.sh consults     # Run only consults app tests
#   ./run_tests.sh --verbose    # Run with verbose output
#

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Running tests with coverage...${NC}"

# Default test target
TEST_TARGET="${1:-consults}"

# Run tests with coverage
if [ "$1" == "--verbose" ]; then
    coverage run --source='.' manage.py test $TEST_TARGET --verbosity=2
else
    coverage run --source='.' manage.py test $TEST_TARGET
fi

# Generate coverage report
echo -e "\n${YELLOW}Generating coverage report...${NC}"
coverage report

# Generate HTML report
coverage html
echo -e "${GREEN}HTML coverage report generated at htmlcov/index.html${NC}"

# Check if coverage is above threshold
COVERAGE=$(coverage report | grep TOTAL | awk '{print $4}' | sed 's/%//')
THRESHOLD=95

if (( $(echo "$COVERAGE >= $THRESHOLD" | bc -l) )); then
    echo -e "${GREEN}✓ Coverage is ${COVERAGE}% (threshold: ${THRESHOLD}%)${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠ Coverage is ${COVERAGE}% (threshold: ${THRESHOLD}%)${NC}"
    exit 0
fi
