#!/usr/bin/env python3
"""
Proof that msgspec constraints run in C and are FAST!
"""

import msgspec
from typing import Annotated
import time

# Define struct with msgspec constraints (runs in C!)
class User(msgspec.Struct):
    username: Annotated[str, msgspec.Meta(min_length=3, max_length=50)]
    age: Annotated[int, msgspec.Meta(ge=18, le=120)]
    email: Annotated[str, msgspec.Meta(pattern=r'^[^@]+@[^@]+\.[^@]+$')]

# Test valid data
print("Testing VALID data:")
try:
    valid_json = b'{"username": "john_doe", "age": 25, "email": "john@example.com"}'
    user = msgspec.json.decode(valid_json, type=User)
    print(f"✅ Valid: {user}")
except msgspec.ValidationError as e:
    print(f"❌ Validation failed: {e}")

# Test invalid age (too young)
print("\nTesting INVALID age (too young):")
try:
    invalid_json = b'{"username": "john_doe", "age": 12, "email": "john@example.com"}'
    user = msgspec.json.decode(invalid_json, type=User)
    print(f"✅ Valid: {user}")
except msgspec.ValidationError as e:
    print(f"❌ Validation failed: {e}")

# Test invalid username (too short)
print("\nTesting INVALID username (too short):")
try:
    invalid_json = b'{"username": "ab", "age": 25, "email": "john@example.com"}'
    user = msgspec.json.decode(invalid_json, type=User)
    print(f"✅ Valid: {user}")
except msgspec.ValidationError as e:
    print(f"❌ Validation failed: {e}")

# Test invalid email pattern
print("\nTesting INVALID email (bad pattern):")
try:
    invalid_json = b'{"username": "john_doe", "age": 25, "email": "not-an-email"}'
    user = msgspec.json.decode(invalid_json, type=User)
    print(f"✅ Valid: {user}")
except msgspec.ValidationError as e:
    print(f"❌ Validation failed: {e}")

# Performance test
print("\n" + "="*60)
print("PERFORMANCE TEST: 10,000 validations")
print("="*60)

valid_json = b'{"username": "john_doe", "age": 25, "email": "john@example.com"}'

# msgspec with constraints (C-level validation)
start = time.perf_counter()
for _ in range(10000):
    user = msgspec.json.decode(valid_json, type=User)
elapsed_c = time.perf_counter() - start

print(f"msgspec constraints (C): {elapsed_c*1000:.2f}ms for 10k = {elapsed_c*100:.2f}μs per item")
print(f"Rate: {10000/elapsed_c:,.0f} validations/second")

# Python validation (for comparison)
class UserNoConstraints(msgspec.Struct):
    username: str
    age: int
    email: str

def validate_python(user):
    if len(user.username) < 3 or len(user.username) > 50:
        raise ValueError("Username must be 3-50 chars")
    if user.age < 18 or user.age > 120:
        raise ValueError("Age must be 18-120")
    if '@' not in user.email or '.' not in user.email:
        raise ValueError("Invalid email")
    return user

start = time.perf_counter()
for _ in range(10000):
    user = msgspec.json.decode(valid_json, type=UserNoConstraints)
    validate_python(user)
elapsed_python = time.perf_counter() - start

print(f"Python validation:      {elapsed_python*1000:.2f}ms for 10k = {elapsed_python*100:.2f}μs per item")
print(f"Rate: {10000/elapsed_python:,.0f} validations/second")

print(f"\n🚀 msgspec is {elapsed_python/elapsed_c:.1f}x FASTER than Python validation!")
