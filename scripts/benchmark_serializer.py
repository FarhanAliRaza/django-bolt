"""
Benchmark: django-bolt Serializer (msgspec) vs Pydantic v2

Comprehensive comparison including scenarios with and without custom field validators.
"""

from __future__ import annotations

import timeit
from typing import Annotated

import msgspec
from msgspec import Meta
from pydantic import BaseModel, Field, field_validator

from django_bolt.serializers import Serializer, field_validator as bolt_field_validator


# ============================================================================
# Test Data
# ============================================================================
SAMPLE_DATA = {
    "id": 1,
    "name": "  John Doe  ",
    "email": "JOHN@EXAMPLE.COM",
    "bio": "Software developer",
}

JSON_STRING = '{"id": 1, "name": "  John Doe  ", "email": "JOHN@EXAMPLE.COM", "bio": "Software developer"}'


# ============================================================================
# Scenario 1: No Custom Field Validators (Pure msgspec vs Pydantic)
# ============================================================================
class BoltAuthorSimple(Serializer):
    """django-bolt serializer WITHOUT custom field validators."""
    id: int
    name: Annotated[str, Meta(min_length=2)]
    email: Annotated[str, Meta(pattern=r"^[^@]+@[^@]+\.[^@]+$")]
    bio: str = ""


class PydanticAuthorSimple(BaseModel):
    """Pydantic model WITHOUT custom field validators."""
    id: int
    name: str = Field(..., min_length=2)
    email: str = Field(..., pattern=r"^[^@]+@[^@]+\.[^@]+$")
    bio: str = ""


# ============================================================================
# Scenario 2: With Custom Field Validators
# ============================================================================
class BoltAuthorWithValidators(Serializer):
    """django-bolt serializer WITH custom field validators."""
    id: int
    name: Annotated[str, Meta(min_length=2)]
    email: Annotated[str, Meta(pattern=r"^[^@]+@[^@]+\.[^@]+$")]
    bio: str = ""

    @bolt_field_validator("name")
    def strip_name(cls, value: str) -> str:
        return value.strip()

    @bolt_field_validator("email")
    def lowercase_email(cls, value: str) -> str:
        return value.lower()


class PydanticAuthorWithValidators(BaseModel):
    """Pydantic model WITH custom field validators."""
    id: int
    name: str = Field(..., min_length=2)
    email: str = Field(..., pattern=r"^[^@]+@[^@]+\.[^@]+$")
    bio: str = ""

    @field_validator("name")
    @classmethod
    def strip_name(cls, v: str) -> str:
        return v.strip()

    @field_validator("email")
    @classmethod
    def lowercase_email(cls, v: str) -> str:
        return v.lower()


# ============================================================================
# Benchmarks
# ============================================================================
def run_benchmarks():
    """Run comprehensive benchmarks."""
    iterations = 100000

    print("=" * 80)
    print("SERIALIZER BENCHMARK: django-bolt (msgspec) vs Pydantic v2")
    print("=" * 80)
    print(f"\nIterations per test: {iterations:,}")
    print("\n")

    # ========================================================================
    # SCENARIO 1: Without Custom Field Validators
    # ========================================================================
    print("=" * 80)
    print("SCENARIO 1: Basic Meta Validation Only (No Custom Validators)")
    print("=" * 80)

    print("\n1. Dict → Object Deserialization")
    print("-" * 80)
    bolt_time = timeit.timeit(
        lambda: msgspec.convert(SAMPLE_DATA, type=BoltAuthorSimple),
        number=iterations
    )
    pydantic_time = timeit.timeit(
        lambda: PydanticAuthorSimple(**SAMPLE_DATA),
        number=iterations
    )
    print(f"  django-bolt: {bolt_time:.4f}s  ({iterations/bolt_time:,.0f} ops/sec)")
    print(f"  Pydantic v2: {pydantic_time:.4f}s  ({iterations/pydantic_time:,.0f} ops/sec)")
    if bolt_time < pydantic_time:
        print(f"  Winner: django-bolt ({pydantic_time/bolt_time:.2f}x faster)")
    else:
        print(f"  Winner: Pydantic v2 ({bolt_time/pydantic_time:.2f}x faster)")

    print("\n2. JSON → Object Deserialization")
    print("-" * 80)
    bolt_time = timeit.timeit(
        lambda: msgspec.json.decode(JSON_STRING, type=BoltAuthorSimple),
        number=iterations
    )
    pydantic_time = timeit.timeit(
        lambda: PydanticAuthorSimple.model_validate_json(JSON_STRING),
        number=iterations
    )
    print(f"  django-bolt: {bolt_time:.4f}s  ({iterations/bolt_time:,.0f} ops/sec)")
    print(f"  Pydantic v2: {pydantic_time:.4f}s  ({iterations/pydantic_time:,.0f} ops/sec)")
    if bolt_time < pydantic_time:
        print(f"  Winner: django-bolt ({pydantic_time/bolt_time:.2f}x faster)")
    else:
        print(f"  Winner: Pydantic v2 ({bolt_time/pydantic_time:.2f}x faster)")

    print("\n3. Object → Dict Serialization")
    print("-" * 80)
    bolt_obj = msgspec.convert(SAMPLE_DATA, type=BoltAuthorSimple)
    pydantic_obj = PydanticAuthorSimple(**SAMPLE_DATA)

    bolt_time = timeit.timeit(lambda: bolt_obj.to_dict(), number=iterations)
    pydantic_time = timeit.timeit(lambda: pydantic_obj.model_dump(), number=iterations)
    print(f"  django-bolt: {bolt_time:.4f}s  ({iterations/bolt_time:,.0f} ops/sec)")
    print(f"  Pydantic v2: {pydantic_time:.4f}s  ({iterations/pydantic_time:,.0f} ops/sec)")
    if bolt_time < pydantic_time:
        print(f"  Winner: django-bolt ({pydantic_time/bolt_time:.2f}x faster)")
    else:
        print(f"  Winner: Pydantic v2 ({bolt_time/pydantic_time:.2f}x faster)")

    print("\n4. Object → JSON Serialization")
    print("-" * 80)
    bolt_time = timeit.timeit(lambda: msgspec.json.encode(bolt_obj), number=iterations)
    pydantic_time = timeit.timeit(lambda: pydantic_obj.model_dump_json(), number=iterations)
    print(f"  django-bolt: {bolt_time:.4f}s  ({iterations/bolt_time:,.0f} ops/sec)")
    print(f"  Pydantic v2: {pydantic_time:.4f}s  ({iterations/pydantic_time:,.0f} ops/sec)")
    if bolt_time < pydantic_time:
        print(f"  Winner: django-bolt ({pydantic_time/bolt_time:.2f}x faster)")
    else:
        print(f"  Winner: Pydantic v2 ({bolt_time/pydantic_time:.2f}x faster)")

    # ========================================================================
    # SCENARIO 2: With Custom Field Validators
    # ========================================================================
    print("\n\n" + "=" * 80)
    print("SCENARIO 2: With Custom Field Validators (strip, lowercase)")
    print("=" * 80)

    print("\n1. Dict → Object Deserialization (with validators)")
    print("-" * 80)
    bolt_time = timeit.timeit(
        lambda: msgspec.convert(SAMPLE_DATA, type=BoltAuthorWithValidators),
        number=iterations
    )
    pydantic_time = timeit.timeit(
        lambda: PydanticAuthorWithValidators(**SAMPLE_DATA),
        number=iterations
    )
    print(f"  django-bolt: {bolt_time:.4f}s  ({iterations/bolt_time:,.0f} ops/sec)")
    print(f"  Pydantic v2: {pydantic_time:.4f}s  ({iterations/pydantic_time:,.0f} ops/sec)")
    if bolt_time < pydantic_time:
        print(f"  Winner: django-bolt ({pydantic_time/bolt_time:.2f}x faster)")
    else:
        print(f"  Winner: Pydantic v2 ({bolt_time/pydantic_time:.2f}x faster)")

    print("\n2. JSON → Object Deserialization (with validators)")
    print("-" * 80)
    bolt_time = timeit.timeit(
        lambda: msgspec.json.decode(JSON_STRING, type=BoltAuthorWithValidators),
        number=iterations
    )
    pydantic_time = timeit.timeit(
        lambda: PydanticAuthorWithValidators.model_validate_json(JSON_STRING),
        number=iterations
    )
    print(f"  django-bolt: {bolt_time:.4f}s  ({iterations/bolt_time:,.0f} ops/sec)")
    print(f"  Pydantic v2: {pydantic_time:.4f}s  ({iterations/pydantic_time:,.0f} ops/sec)")
    if bolt_time < pydantic_time:
        print(f"  Winner: django-bolt ({pydantic_time/bolt_time:.2f}x faster)")
    else:
        print(f"  Winner: Pydantic v2 ({bolt_time/pydantic_time:.2f}x faster)")

    # ========================================================================
    # Validation Error Performance
    # ========================================================================
    print("\n\n" + "=" * 80)
    print("SCENARIO 3: Validation Error Detection Speed")
    print("=" * 80)

    invalid_data = {"id": 1, "name": "X", "email": "invalid"}
    iterations_error = 10000

    def bolt_validate():
        try:
            msgspec.convert(invalid_data, type=BoltAuthorSimple)
        except msgspec.ValidationError:
            pass

    def pydantic_validate():
        try:
            PydanticAuthorSimple(**invalid_data)
        except Exception:
            pass

    bolt_time = timeit.timeit(bolt_validate, number=iterations_error)
    pydantic_time = timeit.timeit(pydantic_validate, number=iterations_error)

    print(f"\nIterations: {iterations_error:,}")
    print("-" * 80)
    print(f"  django-bolt: {bolt_time:.4f}s  ({iterations_error/bolt_time:,.0f} ops/sec)")
    print(f"  Pydantic v2: {pydantic_time:.4f}s  ({iterations_error/pydantic_time:,.0f} ops/sec)")
    if bolt_time < pydantic_time:
        print(f"  Winner: django-bolt ({pydantic_time/bolt_time:.2f}x faster)")
    else:
        print(f"  Winner: Pydantic v2 ({bolt_time/pydantic_time:.2f}x faster)")

    # ========================================================================
    # Summary
    # ========================================================================
    print("\n\n" + "=" * 80)
    print("SUMMARY")
    
    print("=" * 80 + "\n")


if __name__ == "__main__":
    run_benchmarks()
