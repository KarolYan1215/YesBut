#!/bin/bash
# YesBut Full Test Suite Runner
# Usage: ./scripts/run_all_tests.sh

set -e

echo "=========================================="
echo "YesBut Full Test Suite"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track results
BACKEND_RESULT=0
FRONTEND_RESULT=0
E2E_RESULT=0

# Backend Tests
echo -e "\n${YELLOW}[1/3] Running Backend Tests...${NC}"
cd backend
if poetry run pytest -v --tb=short; then
    echo -e "${GREEN}Backend tests passed!${NC}"
else
    echo -e "${RED}Backend tests failed!${NC}"
    BACKEND_RESULT=1
fi
cd ..

# Frontend Unit Tests
echo -e "\n${YELLOW}[2/3] Running Frontend Unit Tests...${NC}"
cd frontend
if npm run test -- --run; then
    echo -e "${GREEN}Frontend unit tests passed!${NC}"
else
    echo -e "${RED}Frontend unit tests failed!${NC}"
    FRONTEND_RESULT=1
fi

# E2E Tests (optional, requires running servers)
if [ "$RUN_E2E" = "true" ]; then
    echo -e "\n${YELLOW}[3/3] Running E2E Tests...${NC}"
    if npx playwright test; then
        echo -e "${GREEN}E2E tests passed!${NC}"
    else
        echo -e "${RED}E2E tests failed!${NC}"
        E2E_RESULT=1
    fi
else
    echo -e "\n${YELLOW}[3/3] Skipping E2E Tests (set RUN_E2E=true to enable)${NC}"
fi
cd ..

# Summary
echo -e "\n=========================================="
echo "Test Summary"
echo "=========================================="
if [ $BACKEND_RESULT -eq 0 ]; then
    echo -e "Backend:  ${GREEN}PASSED${NC}"
else
    echo -e "Backend:  ${RED}FAILED${NC}"
fi

if [ $FRONTEND_RESULT -eq 0 ]; then
    echo -e "Frontend: ${GREEN}PASSED${NC}"
else
    echo -e "Frontend: ${RED}FAILED${NC}"
fi

if [ "$RUN_E2E" = "true" ]; then
    if [ $E2E_RESULT -eq 0 ]; then
        echo -e "E2E:      ${GREEN}PASSED${NC}"
    else
        echo -e "E2E:      ${RED}FAILED${NC}"
    fi
else
    echo -e "E2E:      ${YELLOW}SKIPPED${NC}"
fi

# Exit with error if any test failed
if [ $BACKEND_RESULT -ne 0 ] || [ $FRONTEND_RESULT -ne 0 ] || [ $E2E_RESULT -ne 0 ]; then
    exit 1
fi

echo -e "\n${GREEN}All tests passed!${NC}"
