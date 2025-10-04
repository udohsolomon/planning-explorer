#!/bin/bash
# Test runner script for Planning Explorer
# Provides convenient commands for running different test suites

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}  Planning Explorer Test Suite Runner${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

# Parse command line arguments
TEST_TYPE=${1:-all}
EXTRA_ARGS="${@:2}"

case $TEST_TYPE in

  all)
    echo -e "${GREEN}Running all tests...${NC}"
    pytest tests/ -v $EXTRA_ARGS
    ;;

  unit)
    echo -e "${GREEN}Running unit tests...${NC}"
    pytest -m unit -v $EXTRA_ARGS
    ;;

  integration)
    echo -e "${GREEN}Running integration tests...${NC}"
    pytest -m integration -v $EXTRA_ARGS
    ;;

  live)
    echo -e "${YELLOW}Running tests with live data (requires ES and Supabase)...${NC}"
    pytest -m live_data -v $EXTRA_ARGS
    ;;

  search)
    echo -e "${GREEN}Running search endpoint tests...${NC}"
    pytest -m search -v $EXTRA_ARGS
    ;;

  ai)
    echo -e "${GREEN}Running AI feature tests...${NC}"
    pytest -m ai -v $EXTRA_ARGS
    ;;

  reports)
    echo -e "${GREEN}Running report generation tests...${NC}"
    pytest -m reports -v $EXTRA_ARGS
    ;;

  auth)
    echo -e "${GREEN}Running authentication tests...${NC}"
    pytest -m auth -v $EXTRA_ARGS
    ;;

  performance)
    echo -e "${GREEN}Running performance tests...${NC}"
    pytest -m performance -v -s $EXTRA_ARGS
    ;;

  fast)
    echo -e "${GREEN}Running fast tests only (excluding slow and live_data)...${NC}"
    pytest -m "not slow and not live_data" -v $EXTRA_ARGS
    ;;

  coverage)
    echo -e "${GREEN}Running tests with coverage report...${NC}"
    pytest tests/ --cov=app --cov-report=html --cov-report=term-missing $EXTRA_ARGS
    echo -e "${BLUE}Coverage report generated at: ${NC}htmlcov/index.html"
    ;;

  file)
    if [ -z "$2" ]; then
      echo -e "${RED}Error: Please specify a test file${NC}"
      echo "Usage: ./run_tests.sh file tests/test_search_endpoints.py"
      exit 1
    fi
    echo -e "${GREEN}Running tests from file: $2${NC}"
    pytest "$2" -v "${@:3}"
    ;;

  single)
    if [ -z "$2" ]; then
      echo -e "${RED}Error: Please specify a test${NC}"
      echo "Usage: ./run_tests.sh single tests/test_search_endpoints.py::TestTextSearch::test_basic_search_success"
      exit 1
    fi
    echo -e "${GREEN}Running single test: $2${NC}"
    pytest "$2" -v "${@:3}"
    ;;

  debug)
    echo -e "${YELLOW}Running tests in debug mode (stops at first failure)...${NC}"
    pytest tests/ -v -x --pdb $EXTRA_ARGS
    ;;

  watch)
    echo -e "${GREEN}Running tests in watch mode...${NC}"
    pytest-watch tests/ -- -v $EXTRA_ARGS
    ;;

  ci)
    echo -e "${GREEN}Running CI test suite...${NC}"
    pytest tests/ --cov=app --cov-report=xml --cov-report=term -v $EXTRA_ARGS
    ;;

  help|--help|-h)
    echo "Usage: ./run_tests.sh [TEST_TYPE] [EXTRA_ARGS]"
    echo ""
    echo "TEST_TYPE:"
    echo "  all           - Run all tests (default)"
    echo "  unit          - Run unit tests only"
    echo "  integration   - Run integration tests"
    echo "  live          - Run tests with live Elasticsearch data"
    echo "  search        - Run search endpoint tests"
    echo "  ai            - Run AI feature tests"
    echo "  reports       - Run report generation tests"
    echo "  auth          - Run authentication tests"
    echo "  performance   - Run performance benchmarks"
    echo "  fast          - Run fast tests (exclude slow and live_data)"
    echo "  coverage      - Run with coverage report (HTML)"
    echo "  file [PATH]   - Run specific test file"
    echo "  single [PATH] - Run single test"
    echo "  debug         - Run in debug mode (stop on first failure)"
    echo "  watch         - Run in watch mode (re-run on changes)"
    echo "  ci            - Run CI test suite (XML coverage)"
    echo "  help          - Show this help message"
    echo ""
    echo "EXTRA_ARGS:"
    echo "  Any additional pytest arguments (e.g., -s, -x, -k 'pattern')"
    echo ""
    echo "Examples:"
    echo "  ./run_tests.sh all"
    echo "  ./run_tests.sh search -s"
    echo "  ./run_tests.sh file tests/test_search_endpoints.py"
    echo "  ./run_tests.sh single tests/test_search_endpoints.py::TestTextSearch::test_basic_search_success"
    echo "  ./run_tests.sh coverage"
    echo "  ./run_tests.sh fast -k 'search'"
    ;;

  *)
    echo -e "${RED}Error: Unknown test type '$TEST_TYPE'${NC}"
    echo "Run './run_tests.sh help' for usage information"
    exit 1
    ;;

esac

echo ""
echo -e "${BLUE}================================================${NC}"
echo -e "${GREEN}Test run complete!${NC}"
echo -e "${BLUE}================================================${NC}"
