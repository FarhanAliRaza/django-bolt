"""
Raw benchmark: Pure msgspec vs Pydantic (no wrappers, no validators)
"""

from __future__ import annotations

import timeit
from typing import Annotated

import msgspec
from msgspec import Meta
from pydantic import BaseModel, Field


# ============================================================================
# Test Data
# ============================================================================
SAMPLE_DATA = {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "bio": "Software developer",
}

JSON_STRING = '{"id": 1, "name": "John Doe", "email": "john@example.com", "bio": "Software developer"}'


# ============================================================================
# Raw msgspec.Struct (NO Serializer wrapper)
# ============================================================================
class MsgspecAuthor(msgspec.Struct):
    """Pure msgspec.Struct with Meta constraints."""
    id: int
    name: Annotated[str, Meta(min_length=2)]
    email: Annotated[str, Meta(pattern=r"^[^@]+@[^@]+\.[^@]+$")]
    bio: str = ""


# ============================================================================
# Raw Pydantic BaseModel
# ============================================================================
class PydanticAuthor(BaseModel):
    """Pure Pydantic BaseModel."""
    id: int
    name: str = Field(..., min_length=2)
    email: str = Field(..., pattern=r"^[^@]+@[^@]+\.[^@]+$")
    bio: str = ""


# ============================================================================
# Benchmark
# ============================================================================
def run_benchmark():
    iterations = 100000

    print("=" * 80)
    print("RAW BENCHMARK: Pure msgspec vs Pydantic (No Wrappers, No Custom Validators)")
    print("=" * 80)
    print(f"\nIterations: {iterations:,}\n")

    # ========================================================================
    # Dict → Object Deserialization
    # ========================================================================
    print("1. Dict → Object Deserialization")
    print("-" * 80)

    msgspec_time = timeit.timeit(
        lambda: msgspec.convert(SAMPLE_DATA, type=MsgspecAuthor),
        number=iterations
    )

    pydantic_time = timeit.timeit(
        lambda: PydanticAuthor(**SAMPLE_DATA),
        number=iterations
    )

    print(f"  msgspec:     {msgspec_time:.4f}s  ({iterations/msgspec_time:,.0f} ops/sec)")
    print(f"  Pydantic v2: {pydantic_time:.4f}s  ({iterations/pydantic_time:,.0f} ops/sec)")

    if msgspec_time < pydantic_time:
        print(f"  Winner: msgspec ({pydantic_time/msgspec_time:.2f}x faster)")
    else:
        print(f"  Winner: Pydantic v2 ({msgspec_time/pydantic_time:.2f}x faster)")

    # ========================================================================
    # JSON → Object Deserialization
    # ========================================================================
    print("\n2. JSON → Object Deserialization")
    print("-" * 80)

    msgspec_time = timeit.timeit(
        lambda: msgspec.json.decode(JSON_STRING.encode(), type=MsgspecAuthor),
        number=iterations
    )

    pydantic_time = timeit.timeit(
        lambda: PydanticAuthor.model_validate_json(JSON_STRING),
        number=iterations
    )

    print(f"  msgspec:     {msgspec_time:.4f}s  ({iterations/msgspec_time:,.0f} ops/sec)")
    print(f"  Pydantic v2: {pydantic_time:.4f}s  ({iterations/pydantic_time:,.0f} ops/sec)")

    if msgspec_time < pydantic_time:
        print(f"  Winner: msgspec ({pydantic_time/msgspec_time:.2f}x faster)")
    else:
        print(f"  Winner: Pydantic v2 ({msgspec_time/pydantic_time:.2f}x faster)")

    # ========================================================================
    # Object → Dict Serialization
    # ========================================================================
    print("\n3. Object → Dict Serialization")
    print("-" * 80)

    msgspec_obj = msgspec.convert(SAMPLE_DATA, type=MsgspecAuthor)
    pydantic_obj = PydanticAuthor(**SAMPLE_DATA)

    msgspec_time = timeit.timeit(
        lambda: msgspec.to_builtins(msgspec_obj),
        number=iterations
    )

    pydantic_time = timeit.timeit(
        lambda: pydantic_obj.model_dump(),
        number=iterations
    )

    print(f"  msgspec:     {msgspec_time:.4f}s  ({iterations/msgspec_time:,.0f} ops/sec)")
    print(f"  Pydantic v2: {pydantic_time:.4f}s  ({iterations/pydantic_time:,.0f} ops/sec)")

    if msgspec_time < pydantic_time:
        print(f"  Winner: msgspec ({pydantic_time/msgspec_time:.2f}x faster)")
    else:
        print(f"  Winner: Pydantic v2 ({msgspec_time/pydantic_time:.2f}x faster)")

    # ========================================================================
    # Object → JSON Serialization
    # ========================================================================
    print("\n4. Object → JSON Serialization")
    print("-" * 80)

    msgspec_time = timeit.timeit(
        lambda: msgspec.json.encode(msgspec_obj),
        number=iterations
    )

    pydantic_time = timeit.timeit(
        lambda: pydantic_obj.model_dump_json(),
        number=iterations
    )

    print(f"  msgspec:     {msgspec_time:.4f}s  ({iterations/msgspec_time:,.0f} ops/sec)")
    print(f"  Pydantic v2: {pydantic_time:.4f}s  ({iterations/pydantic_time:,.0f} ops/sec)")

    if msgspec_time < pydantic_time:
        print(f"  Winner: msgspec ({pydantic_time/msgspec_time:.2f}x faster)")
    else:
        print(f"  Winner: Pydantic v2 ({msgspec_time/pydantic_time:.2f}x faster)")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    run_benchmark()
