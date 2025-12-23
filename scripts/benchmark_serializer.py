"""
Benchmark: django-bolt Serializer (msgspec) vs Pydantic v2

Comprehensive comparison including:
- Basic validation (Meta constraints)
- Custom field validators
- Model validators (cross-field validation)
- Computed fields
- field() with read_only/write_only
- Dynamic field selection (only/exclude/use)
- Type-safe subsets (subset/fields methods)
- dump() options (exclude_none, exclude_defaults)
- Reusable validated types (Email, HttpUrl, etc.)
"""

from __future__ import annotations

import contextlib
import timeit
from typing import Annotated

import msgspec
from msgspec import Meta
from pydantic import (
    BaseModel,
    Field,
    field_validator,
    model_validator,
)
from pydantic import (
    computed_field as pydantic_computed_field,
)

from django_bolt.serializers import (
    Serializer,
    computed_field,
    field,
)
from django_bolt.serializers import (
    field_validator as bolt_field_validator,
)
from django_bolt.serializers import (
    model_validator as bolt_model_validator,
)
from django_bolt.serializers.types import Email, HttpsURL, NonEmptyStr, PositiveInt

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

COMPLEX_DATA = {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "website": "https://example.com",
    "age": 30,
    "score": 95.5,
    "tags": ["python", "django"],
    "created_at": "2024-01-15T10:30:00",
}

COMPLEX_JSON = '{"id": 1, "name": "John Doe", "email": "john@example.com", "website": "https://example.com", "age": 30, "score": 95.5, "tags": ["python", "django"], "created_at": "2024-01-15T10:30:00"}'

USER_DATA_WITH_NULLS = {
    "id": 1,
    "name": "John",
    "email": "john@example.com",
    "bio": None,
    "website": None,
    "role": "user",
}


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
# Scenario 3: Model Validators (Cross-Field Validation)
# ============================================================================
class BoltPasswordChange(Serializer):
    """django-bolt serializer with model validator."""
    old_password: str
    new_password: Annotated[str, Meta(min_length=8)]
    confirm_password: str

    @bolt_model_validator
    def validate_passwords(self):
        if self.new_password != self.confirm_password:
            raise ValueError("Passwords don't match")
        if self.old_password == self.new_password:
            raise ValueError("New password must be different")


class PydanticPasswordChange(BaseModel):
    """Pydantic model with model validator."""
    old_password: str
    new_password: str = Field(..., min_length=8)
    confirm_password: str

    @model_validator(mode="after")
    def validate_passwords(self):
        if self.new_password != self.confirm_password:
            raise ValueError("Passwords don't match")
        if self.old_password == self.new_password:
            raise ValueError("New password must be different")
        return self


# ============================================================================
# Scenario 4: Computed Fields
# ============================================================================
class BoltUserWithComputed(Serializer):
    """django-bolt serializer with computed fields."""
    first_name: str
    last_name: str
    email: str

    @computed_field
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @computed_field
    def initials(self) -> str:
        return f"{self.first_name[0]}{self.last_name[0]}".upper()


class PydanticUserWithComputed(BaseModel):
    """Pydantic model with computed fields."""
    first_name: str
    last_name: str
    email: str

    @pydantic_computed_field
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @pydantic_computed_field
    @property
    def initials(self) -> str:
        return f"{self.first_name[0]}{self.last_name[0]}".upper()


# ============================================================================
# Scenario 5: field() with read_only/write_only
# ============================================================================
class BoltUserWithFieldConfig(Serializer):
    """django-bolt serializer with field() configuration."""
    id: int = field(read_only=True, default=0)
    name: Annotated[str, Meta(min_length=1, max_length=100)]
    email: str
    password: str = field(write_only=True, default="")
    created_at: str = field(read_only=True, default="")


class PydanticUserWithFieldConfig(BaseModel):
    """Pydantic model with Field() configuration."""
    id: int = Field(default=0)  # Can't really do read_only in Pydantic
    name: str = Field(..., min_length=1, max_length=100)
    email: str
    password: str = Field(default="", exclude=True)  # write_only equivalent
    created_at: str = Field(default="")


# ============================================================================
# Scenario 6: Dynamic Field Selection (only/exclude/use)
# ============================================================================
class BoltUserDynamic(Serializer):
    """django-bolt serializer with field sets for dynamic selection."""
    id: int
    name: str
    email: str
    password: str = ""
    created_at: str = ""
    internal_notes: str = ""

    class Config:
        write_only = {"password"}
        field_sets = {
            "list": ["id", "name", "email"],
            "detail": ["id", "name", "email", "created_at"],
            "admin": ["id", "name", "email", "created_at", "internal_notes"],
        }


class PydanticUserDynamic(BaseModel):
    """Pydantic model - note: Pydantic doesn't have built-in field_sets."""
    id: int
    name: str
    email: str
    password: str = Field(default="", exclude=True)
    created_at: str = ""
    internal_notes: str = ""


# ============================================================================
# Scenario 7: Reusable Validated Types
# ============================================================================
class BoltUserWithTypes(Serializer):
    """django-bolt serializer using reusable validated types."""
    id: PositiveInt
    name: NonEmptyStr
    email: Email
    website: HttpsURL | None = None


class PydanticUserWithTypes(BaseModel):
    """Pydantic model with equivalent constraints."""
    id: int = Field(..., gt=0)
    name: str = Field(..., min_length=1)
    email: str = Field(..., pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    website: str | None = Field(default=None, pattern=r"^https?://[^\s/$.?#].[^\s]*$")


# ============================================================================
# Scenario 8: Complex Nested Data
# ============================================================================
class BoltComplexUser(Serializer):
    """django-bolt serializer with multiple field types."""
    id: int
    name: Annotated[str, Meta(min_length=1, max_length=100)]
    email: str
    age: Annotated[int, Meta(ge=0, le=150)]
    score: Annotated[float, Meta(ge=0, le=100)]
    website: str | None = None
    tags: list[str] = []
    created_at: str = ""


class PydanticComplexUser(BaseModel):
    """Pydantic model with multiple field types."""
    id: int
    name: str = Field(..., min_length=1, max_length=100)
    email: str
    website: str | None = None
    age: int = Field(..., ge=0, le=150)
    score: float = Field(..., ge=0, le=100)
    tags: list[str] = []
    created_at: str = ""


# ============================================================================
# Benchmarks
# ============================================================================
def run_benchmarks():
    """Run comprehensive benchmarks."""
    iterations = 100000

    print("=" * 80)
    print("SERIALIZER BENCHMARK: django-bolt (msgspec) vs Pydantic v2")
    print("=" * 80)
    print(f"\nDefault iterations: {iterations:,}")
    print("\n")

    # ========================================================================
    # SCENARIO 1: Without Custom Field Validators
    # ========================================================================
    print("=" * 80)
    print("SCENARIO 1: Basic Meta Validation Only (No Custom Validators)")
    print("=" * 80)

    print("\n1. Dict -> Object Deserialization")
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
    print_winner(bolt_time, pydantic_time)

    print("\n2. JSON -> Object Deserialization")
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
    print_winner(bolt_time, pydantic_time)

    print("\n3. Object -> Dict Serialization (to_dict/model_dump)")
    print("-" * 80)
    bolt_obj = msgspec.convert(SAMPLE_DATA, type=BoltAuthorSimple)
    pydantic_obj = PydanticAuthorSimple(**SAMPLE_DATA)

    bolt_time = timeit.timeit(lambda: bolt_obj.to_dict(), number=iterations)
    pydantic_time = timeit.timeit(lambda: pydantic_obj.model_dump(), number=iterations)
    print(f"  django-bolt: {bolt_time:.4f}s  ({iterations/bolt_time:,.0f} ops/sec)")
    print(f"  Pydantic v2: {pydantic_time:.4f}s  ({iterations/pydantic_time:,.0f} ops/sec)")
    print_winner(bolt_time, pydantic_time)

    print("\n4. Object -> JSON Serialization")
    print("-" * 80)
    bolt_time = timeit.timeit(lambda: msgspec.json.encode(bolt_obj), number=iterations)
    pydantic_time = timeit.timeit(lambda: pydantic_obj.model_dump_json(), number=iterations)
    print(f"  django-bolt: {bolt_time:.4f}s  ({iterations/bolt_time:,.0f} ops/sec)")
    print(f"  Pydantic v2: {pydantic_time:.4f}s  ({iterations/pydantic_time:,.0f} ops/sec)")
    print_winner(bolt_time, pydantic_time)

    # ========================================================================
    # SCENARIO 2: With Custom Field Validators
    # ========================================================================
    print("\n\n" + "=" * 80)
    print("SCENARIO 2: With Custom Field Validators (strip, lowercase)")
    print("=" * 80)

    print("\n1. Dict -> Object Deserialization (with validators)")
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
    print_winner(bolt_time, pydantic_time)

    print("\n2. JSON -> Object Deserialization (with validators)")
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
    print_winner(bolt_time, pydantic_time)

    # ========================================================================
    # SCENARIO 3: Model Validators (Cross-Field Validation)
    # ========================================================================
    print("\n\n" + "=" * 80)
    print("SCENARIO 3: Model Validators (Cross-Field Validation)")
    print("=" * 80)

    password_data = {
        "old_password": "oldpass123",
        "new_password": "newpass123",
        "confirm_password": "newpass123",
    }

    print("\n1. Dict -> Object with Model Validator")
    print("-" * 80)
    bolt_time = timeit.timeit(
        lambda: msgspec.convert(password_data, type=BoltPasswordChange),
        number=iterations
    )
    pydantic_time = timeit.timeit(
        lambda: PydanticPasswordChange(**password_data),
        number=iterations
    )
    print(f"  django-bolt: {bolt_time:.4f}s  ({iterations/bolt_time:,.0f} ops/sec)")
    print(f"  Pydantic v2: {pydantic_time:.4f}s  ({iterations/pydantic_time:,.0f} ops/sec)")
    print_winner(bolt_time, pydantic_time)

    # ========================================================================
    # SCENARIO 4: Computed Fields
    # ========================================================================
    print("\n\n" + "=" * 80)
    print("SCENARIO 4: Computed Fields")
    print("=" * 80)

    user_data = {"first_name": "John", "last_name": "Doe", "email": "john@example.com"}

    print("\n1. Object Creation with Computed Fields")
    print("-" * 80)
    bolt_time = timeit.timeit(
        lambda: msgspec.convert(user_data, type=BoltUserWithComputed),
        number=iterations
    )
    pydantic_time = timeit.timeit(
        lambda: PydanticUserWithComputed(**user_data),
        number=iterations
    )
    print(f"  django-bolt: {bolt_time:.4f}s  ({iterations/bolt_time:,.0f} ops/sec)")
    print(f"  Pydantic v2: {pydantic_time:.4f}s  ({iterations/pydantic_time:,.0f} ops/sec)")
    print_winner(bolt_time, pydantic_time)

    print("\n2. Dump with Computed Fields")
    print("-" * 80)
    bolt_user = msgspec.convert(user_data, type=BoltUserWithComputed)
    pydantic_user = PydanticUserWithComputed(**user_data)

    bolt_time = timeit.timeit(lambda: bolt_user.dump(), number=iterations)
    pydantic_time = timeit.timeit(lambda: pydantic_user.model_dump(), number=iterations)
    print(f"  django-bolt: {bolt_time:.4f}s  ({iterations/bolt_time:,.0f} ops/sec)")
    print(f"  Pydantic v2: {pydantic_time:.4f}s  ({iterations/pydantic_time:,.0f} ops/sec)")
    print_winner(bolt_time, pydantic_time)

    # ========================================================================
    # SCENARIO 5: field() with read_only/write_only
    # ========================================================================
    print("\n\n" + "=" * 80)
    print("SCENARIO 5: field() Configuration (read_only/write_only)")
    print("=" * 80)

    field_data = {"id": 1, "name": "John", "email": "john@example.com", "password": "secret"}

    print("\n1. Object Creation with field() Config")
    print("-" * 80)
    bolt_time = timeit.timeit(
        lambda: msgspec.convert(field_data, type=BoltUserWithFieldConfig),
        number=iterations
    )
    pydantic_time = timeit.timeit(
        lambda: PydanticUserWithFieldConfig(**field_data),
        number=iterations
    )
    print(f"  django-bolt: {bolt_time:.4f}s  ({iterations/bolt_time:,.0f} ops/sec)")
    print(f"  Pydantic v2: {pydantic_time:.4f}s  ({iterations/pydantic_time:,.0f} ops/sec)")
    print_winner(bolt_time, pydantic_time)

    print("\n2. Dump with write_only Exclusion")
    print("-" * 80)
    bolt_field_user = msgspec.convert(field_data, type=BoltUserWithFieldConfig)
    pydantic_field_user = PydanticUserWithFieldConfig(**field_data)

    bolt_time = timeit.timeit(lambda: bolt_field_user.dump(), number=iterations)
    pydantic_time = timeit.timeit(lambda: pydantic_field_user.model_dump(), number=iterations)
    print(f"  django-bolt: {bolt_time:.4f}s  ({iterations/bolt_time:,.0f} ops/sec)")
    print(f"  Pydantic v2: {pydantic_time:.4f}s  ({iterations/pydantic_time:,.0f} ops/sec)")
    print_winner(bolt_time, pydantic_time)

    # ========================================================================
    # SCENARIO 6: Dynamic Field Selection
    # ========================================================================
    print("\n\n" + "=" * 80)
    print("SCENARIO 6: Dynamic Field Selection (only/exclude/use)")
    print("=" * 80)

    dynamic_data = {
        "id": 1, "name": "John", "email": "john@example.com",
        "password": "secret", "created_at": "2024-01-15", "internal_notes": "VIP"
    }

    bolt_dynamic = msgspec.convert(dynamic_data, type=BoltUserDynamic)
    pydantic_dynamic = PydanticUserDynamic(**dynamic_data)

    print("\n1. only() - Include specific fields (3 fields)")
    print("-" * 80)
    bolt_time = timeit.timeit(
        lambda: BoltUserDynamic.only("id", "name", "email").dump(bolt_dynamic),
        number=iterations
    )
    # Pydantic: use include in model_dump
    pydantic_time = timeit.timeit(
        lambda: pydantic_dynamic.model_dump(include={"id", "name", "email"}),
        number=iterations
    )
    print(f"  django-bolt: {bolt_time:.4f}s  ({iterations/bolt_time:,.0f} ops/sec)")
    print(f"  Pydantic v2: {pydantic_time:.4f}s  ({iterations/pydantic_time:,.0f} ops/sec)")
    print_winner(bolt_time, pydantic_time)

    print("\n2. exclude() - Exclude specific fields")
    print("-" * 80)
    bolt_time = timeit.timeit(
        lambda: BoltUserDynamic.exclude("password", "internal_notes").dump(bolt_dynamic),
        number=iterations
    )
    pydantic_time = timeit.timeit(
        lambda: pydantic_dynamic.model_dump(exclude={"password", "internal_notes"}),
        number=iterations
    )
    print(f"  django-bolt: {bolt_time:.4f}s  ({iterations/bolt_time:,.0f} ops/sec)")
    print(f"  Pydantic v2: {pydantic_time:.4f}s  ({iterations/pydantic_time:,.0f} ops/sec)")
    print_winner(bolt_time, pydantic_time)

    print("\n3. use() - Predefined field sets")
    print("-" * 80)
    # Pre-create view for fair comparison
    list_view = BoltUserDynamic.use("list")
    bolt_time = timeit.timeit(
        lambda: list_view.dump(bolt_dynamic),
        number=iterations
    )
    pydantic_time = timeit.timeit(
        lambda: pydantic_dynamic.model_dump(include={"id", "name", "email"}),
        number=iterations
    )
    print(f"  django-bolt: {bolt_time:.4f}s  ({iterations/bolt_time:,.0f} ops/sec)")
    print(f"  Pydantic v2: {pydantic_time:.4f}s  ({iterations/pydantic_time:,.0f} ops/sec)")
    print_winner(bolt_time, pydantic_time)

    # ========================================================================
    # SCENARIO 8: Dump Options (exclude_none, exclude_defaults)
    # ========================================================================
    print("\n\n" + "=" * 80)
    print("SCENARIO 8: Dump Options (exclude_none, exclude_defaults)")
    print("=" * 80)

    class BoltUserNullable(Serializer):
        id: int
        name: str
        email: str
        bio: str | None = None
        website: str | None = None
        role: str = "user"

    class PydanticUserNullable(BaseModel):
        id: int
        name: str
        email: str
        bio: str | None = None
        website: str | None = None
        role: str = "user"

    nullable_data = {"id": 1, "name": "John", "email": "john@example.com", "bio": None, "website": None, "role": "user"}
    bolt_nullable = msgspec.convert(nullable_data, type=BoltUserNullable)
    pydantic_nullable = PydanticUserNullable(**nullable_data)

    print("\n1. dump(exclude_none=True)")
    print("-" * 80)
    bolt_time = timeit.timeit(
        lambda: bolt_nullable.dump(exclude_none=True),
        number=iterations
    )
    pydantic_time = timeit.timeit(
        lambda: pydantic_nullable.model_dump(exclude_none=True),
        number=iterations
    )
    print(f"  django-bolt: {bolt_time:.4f}s  ({iterations/bolt_time:,.0f} ops/sec)")
    print(f"  Pydantic v2: {pydantic_time:.4f}s  ({iterations/pydantic_time:,.0f} ops/sec)")
    print_winner(bolt_time, pydantic_time)

    print("\n2. dump(exclude_defaults=True)")
    print("-" * 80)
    bolt_time = timeit.timeit(
        lambda: bolt_nullable.dump(exclude_defaults=True),
        number=iterations
    )
    pydantic_time = timeit.timeit(
        lambda: pydantic_nullable.model_dump(exclude_defaults=True),
        number=iterations
    )
    print(f"  django-bolt: {bolt_time:.4f}s  ({iterations/bolt_time:,.0f} ops/sec)")
    print(f"  Pydantic v2: {pydantic_time:.4f}s  ({iterations/pydantic_time:,.0f} ops/sec)")
    print_winner(bolt_time, pydantic_time)

    # ========================================================================
    # SCENARIO 9: Reusable Validated Types
    # ========================================================================
    print("\n\n" + "=" * 80)
    print("SCENARIO 9: Reusable Validated Types (Email, HttpUrl, PositiveInt)")
    print("=" * 80)

    type_data = {"id": 1, "name": "John", "email": "john@example.com", "website": "https://example.com"}

    print("\n1. Dict -> Object with Validated Types")
    print("-" * 80)
    bolt_time = timeit.timeit(
        lambda: msgspec.convert(type_data, type=BoltUserWithTypes),
        number=iterations
    )
    pydantic_time = timeit.timeit(
        lambda: PydanticUserWithTypes(**type_data),
        number=iterations
    )
    print(f"  django-bolt: {bolt_time:.4f}s  ({iterations/bolt_time:,.0f} ops/sec)")
    print(f"  Pydantic v2: {pydantic_time:.4f}s  ({iterations/pydantic_time:,.0f} ops/sec)")
    print_winner(bolt_time, pydantic_time)

    # ========================================================================
    # SCENARIO 10: Complex Nested Data
    # ========================================================================
    print("\n\n" + "=" * 80)
    print("SCENARIO 10: Complex Data (Multiple Types)")
    print("=" * 80)

    print("\n1. Dict -> Object (Complex)")
    print("-" * 80)
    bolt_time = timeit.timeit(
        lambda: msgspec.convert(COMPLEX_DATA, type=BoltComplexUser),
        number=iterations
    )
    pydantic_time = timeit.timeit(
        lambda: PydanticComplexUser(**COMPLEX_DATA),
        number=iterations
    )
    print(f"  django-bolt: {bolt_time:.4f}s  ({iterations/bolt_time:,.0f} ops/sec)")
    print(f"  Pydantic v2: {pydantic_time:.4f}s  ({iterations/pydantic_time:,.0f} ops/sec)")
    print_winner(bolt_time, pydantic_time)

    print("\n2. JSON -> Object (Complex)")
    print("-" * 80)
    bolt_time = timeit.timeit(
        lambda: msgspec.json.decode(COMPLEX_JSON, type=BoltComplexUser),
        number=iterations
    )
    pydantic_time = timeit.timeit(
        lambda: PydanticComplexUser.model_validate_json(COMPLEX_JSON),
        number=iterations
    )
    print(f"  django-bolt: {bolt_time:.4f}s  ({iterations/bolt_time:,.0f} ops/sec)")
    print(f"  Pydantic v2: {pydantic_time:.4f}s  ({iterations/pydantic_time:,.0f} ops/sec)")
    print_winner(bolt_time, pydantic_time)

    # ========================================================================
    # SCENARIO 11: Validation Error Performance
    # ========================================================================
    print("\n\n" + "=" * 80)
    print("SCENARIO 11: Validation Error Detection Speed")
    print("=" * 80)

    invalid_data = {"id": 1, "name": "X", "email": "invalid"}
    iterations_error = 10000

    def bolt_validate():
        with contextlib.suppress(msgspec.ValidationError):
            msgspec.convert(invalid_data, type=BoltAuthorSimple)

    def pydantic_validate():
        with contextlib.suppress(Exception):
            PydanticAuthorSimple(**invalid_data)

    bolt_time = timeit.timeit(bolt_validate, number=iterations_error)
    pydantic_time = timeit.timeit(pydantic_validate, number=iterations_error)

    print(f"\nIterations: {iterations_error:,}")
    print("-" * 80)
    print(f"  django-bolt: {bolt_time:.4f}s  ({iterations_error/bolt_time:,.0f} ops/sec)")
    print(f"  Pydantic v2: {pydantic_time:.4f}s  ({iterations_error/pydantic_time:,.0f} ops/sec)")
    print_winner(bolt_time, pydantic_time)

    # ========================================================================
    # SCENARIO 12: Bulk Operations (dump_many)
    # ========================================================================
    print("\n\n" + "=" * 80)
    print("SCENARIO 12: Bulk Operations (dump_many)")
    print("=" * 80)

    # Create 100 instances
    bolt_instances = [msgspec.convert(SAMPLE_DATA, type=BoltAuthorSimple) for _ in range(100)]
    pydantic_instances = [PydanticAuthorSimple(**SAMPLE_DATA) for _ in range(100)]

    print("\n1. dump_many (100 instances)")
    print("-" * 80)
    iterations_bulk = 10000
    bolt_time = timeit.timeit(
        lambda: BoltAuthorSimple.dump_many(bolt_instances),
        number=iterations_bulk
    )
    pydantic_time = timeit.timeit(
        lambda: [p.model_dump() for p in pydantic_instances],
        number=iterations_bulk
    )
    print(f"  Iterations: {iterations_bulk:,}")
    print(f"  django-bolt: {bolt_time:.4f}s  ({iterations_bulk/bolt_time:,.0f} ops/sec)")
    print(f"  Pydantic v2: {pydantic_time:.4f}s  ({iterations_bulk/pydantic_time:,.0f} ops/sec)")
    print_winner(bolt_time, pydantic_time)

    # ========================================================================
    # Summary
    # ========================================================================
    print("\n\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80 + "\n")
    print("django-bolt Serializer is built on msgspec.Struct which provides:")
    print("  - Zero-copy JSON parsing")
    print("  - C-level struct performance")
    print("  - Minimal validation overhead")
    print("\nAdvanced features (field(), computed_field, dynamic selection)")
    print("add minimal overhead while providing Pydantic-like DX.")
    print()


def print_winner(bolt_time: float, pydantic_time: float) -> None:
    """Print the winner of a benchmark."""
    if bolt_time < pydantic_time:
        print(f"  Winner: django-bolt ({pydantic_time/bolt_time:.2f}x faster)")
    else:
        print(f"  Winner: Pydantic v2 ({bolt_time/pydantic_time:.2f}x faster)")


if __name__ == "__main__":
    run_benchmarks()
