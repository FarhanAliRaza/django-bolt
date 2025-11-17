#!/bin/bash
# Test script for sync dispatch MVP

set -e

echo "========================================="
echo "Testing Sync Dispatch MVP"
echo "========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

BASE_URL="http://127.0.0.1:8000/test-sync"

# Test 1: Basic sync handler
echo "Test 1: Basic sync handler"
response=$(curl -s "$BASE_URL/sync")
echo "Response: $response"
if echo "$response" | grep -q "sync"; then
    echo -e "${GREEN}✓ PASS${NC}"
else
    echo -e "${RED}✗ FAIL${NC}"
fi
echo ""

# Test 2: Async handler (for comparison)
echo "Test 2: Async handler (for comparison)"
response=$(curl -s "$BASE_URL/async")
echo "Response: $response"
if echo "$response" | grep -q "async"; then
    echo -e "${GREEN}✓ PASS${NC}"
else
    echo -e "${RED}✗ FAIL${NC}"
fi
echo ""

# Test 3: Path parameter
echo "Test 3: Path parameter extraction"
response=$(curl -s "$BASE_URL/sync/123")
echo "Response: $response"
if echo "$response" | grep -q "123"; then
    echo -e "${GREEN}✓ PASS${NC}"
else
    echo -e "${RED}✗ FAIL${NC}"
fi
echo ""

# Test 4: Query parameters
echo "Test 4: Query parameter extraction"
response=$(curl -s "$BASE_URL/sync/query?page=2&limit=20&search=test")
echo "Response: $response"
if echo "$response" | grep -q "page.*2" && echo "$response" | grep -q "search.*test"; then
    echo -e "${GREEN}✓ PASS${NC}"
else
    echo -e "${RED}✗ FAIL${NC}"
fi
echo ""

# Test 5: Headers
echo "Test 5: Header extraction"
response=$(curl -s -H "User-Agent: TestBot/1.0" -H "X-Request-ID: abc123" "$BASE_URL/sync/headers")
echo "Response: $response"
if echo "$response" | grep -q "TestBot" && echo "$response" | grep -q "abc123"; then
    echo -e "${GREEN}✓ PASS${NC}"
else
    echo -e "${RED}✗ FAIL${NC}"
fi
echo ""

# Test 6: Request body validation
echo "Test 6: Request body validation (POST)"
response=$(curl -s -X POST "$BASE_URL/sync/items" \
    -H "Content-Type: application/json" \
    -d '{"name": "Test Item", "description": "A test item", "price": 29.99, "quantity": 5}')
echo "Response: $response"
if echo "$response" | grep -q "Test Item" && echo "$response" | grep -q "149.95"; then
    echo -e "${GREEN}✓ PASS${NC}"
else
    echo -e "${RED}✗ FAIL${NC}"
fi
echo ""

# Test 7: msgspec struct response
echo "Test 7: msgspec struct response"
response=$(curl -s "$BASE_URL/sync/struct")
echo "Response: $response"
if echo "$response" | grep -q "Sync with struct" && echo "$response" | grep -q "100"; then
    echo -e "${GREEN}✓ PASS${NC}"
else
    echo -e "${RED}✗ FAIL${NC}"
fi
echo ""

# Test 8: JSON response wrapper
echo "Test 8: JSON response wrapper"
response=$(curl -s "$BASE_URL/sync/json")
echo "Response: $response"
if echo "$response" | grep -q "JSON response"; then
    echo -e "${GREEN}✓ PASS${NC}"
else
    echo -e "${RED}✗ FAIL${NC}"
fi
echo ""

# Test 9: PlainText response
echo "Test 9: PlainText response"
response=$(curl -s "$BASE_URL/sync/text")
echo "Response: $response"
if echo "$response" | grep -q "plain text"; then
    echo -e "${GREEN}✓ PASS${NC}"
else
    echo -e "${RED}✗ FAIL${NC}"
fi
echo ""

# Test 10: HTML response
echo "Test 10: HTML response"
response=$(curl -s "$BASE_URL/sync/html")
echo "Response: $response"
if echo "$response" | grep -q "<h1>Hello from sync handler</h1>"; then
    echo -e "${GREEN}✓ PASS${NC}"
else
    echo -e "${RED}✗ FAIL${NC}"
fi
echo ""

# Test 11: Complex mixed parameters
echo "Test 11: Complex mixed parameters (path + body + headers + query)"
response=$(curl -s -X POST "$BASE_URL/sync/complex/42?debug=true" \
    -H "Content-Type: application/json" \
    -H "Api-Key: secret123" \
    -d '{"name": "Widget", "price": 9.99, "quantity": 10}')
echo "Response: $response"
if echo "$response" | grep -q "user_id.*42" && echo "$response" | grep -q "Widget" && echo "$response" | grep -q "debug.*true"; then
    echo -e "${GREEN}✓ PASS${NC}"
else
    echo -e "${RED}✗ FAIL${NC}"
fi
echo ""

echo "========================================="
echo "All tests completed!"
echo "========================================="
