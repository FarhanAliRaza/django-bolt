from __future__ import annotations

from datetime import datetime
from typing import Annotated

from django_bolt.serializers import (
    Serializer,
    Meta,
    field,
    field_validator,
    model_validator,
    computed_field,
    Nested,
    Email,
    Slug,
    PositiveInt,
    PositiveFloat,
    Percentage,
    NonEmptyStr,
    URL
)

class AuthorSerializer(Serializer):
    """Serializer for Author model with computed field."""

    id: int
    name: NonEmptyStr
    email: Email
    bio: str = ""

    @computed_field
    def display_name(self) -> str:
        return f"{self.name} <{self.email}>"

class TagSerializer(Serializer):
    """Simple serializer for Tag model."""

    id: int
    name: str
    description: str = ""


class ComprehensiveProductSerializer(Serializer):
   
    id: int = field(read_only=True, description="Auto-generated product ID")

    name: NonEmptyStr

    sku: Annotated[str, Meta(pattern=r"^[A-Z]{2,4}-[0-9]{4,8}$", description="Stock Keeping Unit")]

    description: Annotated[str, Meta(max_length=2000)] = field(
        alias="desc",
        default="",
        description="Product description",
    )

    price: Annotated[float, Meta(ge=0.0, description="Product price in USD")]
    quantity: PositiveInt  # Must be > 0
    discount_percent: Percentage = 0.0  # 0-100 range

    internal_cost: float = field(write_only=True, default=0.0)

    category_name: str = field(source="category.name", default="Uncategorized")

    tags_list: list[str] = field(default_factory=list)

    website: URL | None = None
    manufacturer_email: Email | None = None

    created_at: datetime | None = field(read_only=True, default=None)
    updated_at: datetime | None = field(read_only=True, default=None)

    is_active: bool = True
    
    supplier: Annotated[AuthorSerializer | None, Nested(AuthorSerializer)] = None

    related_tags: Annotated[list[TagSerializer], Nested(TagSerializer, many=True)] = field(
        default_factory=list
    )
    class Meta:
        # Fields only in output, never accepted in input
        read_only = {"id", "created_at", "updated_at"}

        # Fields only in input, never in output
        write_only = {"internal_cost"}

        # Predefined field sets for different views
        field_sets = {
            "list": ["id", "name", "sku", "price", "is_active"],
            "detail": [
                "id", "name", "sku", "description", "price", "quantity",
                "discount_percent", "website", "is_active", "is_featured",
                "created_at", "updated_at"
            ],
            "admin": [
                "id", "name", "sku", "description", "price", "quantity",
                "discount_percent", "internal_cost", "category_name",
                "tags_list", "website", "manufacturer_email", "is_active",
                "is_featured", "supplier", "related_tags", "created_at", "updated_at",
                # Include computed fields explicitly
                "display_price", "is_on_sale", "tag_count"
            ],
            "export": ["id", "name", "sku", "price", "quantity", "is_active"],
        }

    # -------------------------------------------------------------------------
    # 14. @field_validator - Transform/validate individual fields
    # -------------------------------------------------------------------------
    @field_validator("name")
    def normalize_name(cls, value: str) -> str:
        """Normalize product name: strip whitespace, title case."""
        return value.strip().title()

    @field_validator("sku")
    def uppercase_sku(cls, value: str) -> str:
        """Ensure SKU is uppercase."""
        return value.upper()

    @field_validator("manufacturer_email")
    def lowercase_email(cls, value: str | None) -> str | None:
        """Normalize email to lowercase."""
        if value is not None:
            return value.lower()
        return value

    # -------------------------------------------------------------------------
    # 15. @model_validator - Cross-field validation
    # -------------------------------------------------------------------------
    @model_validator
    def validate_pricing(self) -> "ComprehensiveProductSerializer":
        """Ensure discount doesn't exceed price logic."""
        if self.discount_percent > 0 and self.price <= 0:
            raise ValueError("Cannot apply discount to zero-priced product")
        if self.discount_percent >= 100:
            raise ValueError("Discount cannot be 100% or more")
        return self

    # -------------------------------------------------------------------------
    # 16. @computed_field - Calculated output-only fields
    # -------------------------------------------------------------------------
    @computed_field
    def display_price(self) -> str:
        """Formatted price string."""
        return f"${self.price:.2f}"

    @computed_field
    def is_on_sale(self) -> bool:
        """Whether product has an active discount."""
        return self.discount_percent > 0

    @computed_field
    def discounted_price(self) -> float | None:
        """Price after discount, or None if no discount."""
        if self.discount_percent > 0:
            return round(self.price * (1 - self.discount_percent / 100), 2)
        return None

    @computed_field
    def tag_count(self) -> int:
        """Number of tags."""
        return len(self.tags_list)

    @computed_field
    def full_title(self) -> str:
        """Full product title with SKU."""
        return f"{self.name} ({self.sku})"

