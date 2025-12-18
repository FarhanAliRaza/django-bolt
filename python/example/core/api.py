import random
import uuid
from typing import Annotated, Literal

import msgspec
from msgspec import Meta

from core.models import Author, Blog
from django_bolt import BoltAPI
from django_bolt.serializers import ModelSerializer, Serializer
from django_bolt.serializers.decorators import computed_field, field_validator, model_validator
from django_bolt.serializers.fields import field


# Raw msgspec struct - no validation overhead, maximum performance
class BlogRaw(msgspec.Struct):
    id: int
    name: str
    description: str
    status: str
    author: int | None


api = BoltAPI(
    prefix="/blogs"
)


class AuthorSerializer(ModelSerializer):
    class Meta:
        model = Author
        fields = ["id", "name", "email", "bio", "created_at"]
        read_only = {"id", "created_at"}


class AuthorUpdateSerializer(ModelSerializer):
    """Serializer for partial updates - all fields optional."""
    class Meta:
        model = Author
        fields = ["name", "email", "bio"]


class BlogSerializer(ModelSerializer):
    class Meta:
        model = Blog
        fields = ["id", "name", "description", "status", "author"]
        read_only = {"id"}
        

class BlogUpdateSerializer(ModelSerializer):
    """Serializer for partial updates - all fields optional."""
    class Meta:
        model = Blog
        fields = ["name", "description", "status", "author"]


class SeedResult(Serializer):
    authors_created: int
    blogs_created: int
    message: str


# Blog endpoints (prefix="/blogs" so these become /blogs/, /blogs/{id}, etc.)
@api.get("")
async def get_blogs() -> list[BlogSerializer]:
    blogs = [blog async for blog in Blog.objects.select_related("author").filter(status="published")[:10]]
    return [BlogSerializer.from_model(b) for b in blogs]


@api.get("/raw")
async def get_blogs_raw() -> list[BlogRaw]:
    """Raw msgspec.Struct - bypasses Serializer for maximum performance."""
    blogs = [blog async for blog in Blog.objects.filter(status="published")[:10]]
    return [
        BlogRaw(
            id=b.id,
            name=b.name,
            description=b.description,
            status=b.status,
            author=b.author_id,
        )
        for b in blogs
    ]


# ============================================
# Django-Bolt Serializer (non-Model, manual)
# Showcasing ALL Serializer features
# ============================================

# Status choices as Literal type
BlogStatus = Literal["published", "draft"]


class BlogBoltSerializer(Serializer):
    """
    Full-featured Serializer example demonstrating:
    - field() with read_only, default
    - Literal for choices validation
    - Annotated with Meta for constraints (min_length, max_length)
    - @field_validator for custom validation
    - @model_validator for cross-field validation
    - @computed_field for derived fields
    - Config with field_sets
    """

    # read_only field - only in output, not required for input
    id: int = field(read_only=True, default=0)

    # Constrained string field with min/max length
    name: Annotated[str, Meta(min_length=1, max_length=255)]

    # Regular string field
    description: str

    # Literal type for choices - validates against allowed values
    status: BlogStatus = "draft"

    # Optional foreign key
    author: int | None = None

    class Config:
        """Configuration with field sets for dynamic field selection."""
        field_sets = {
            "list": ["id", "name", "status"],
            "detail": ["id", "name", "description", "status", "author", "summary"],
        }

    @field_validator("name")
    def validate_name(cls, value: str) -> str:
        """Strip whitespace and ensure not empty."""
        value = value.strip()
        if not value:
            raise ValueError("Name cannot be empty or whitespace only")
        return value

    @field_validator("description")
    def validate_description(cls, value: str) -> str:
        """Strip whitespace from description."""
        return value.strip()

    @model_validator
    def validate_published_has_content(self):
        """Ensure published blogs have a description."""
        if self.status == "published" and len(self.description) < 10:
            raise ValueError("Published blogs must have a description of at least 10 characters")

    @computed_field
    def summary(self) -> str:
        """Return first 50 chars of description."""
        if len(self.description) > 50:
            return self.description[:50] + "..."
        return self.description


class BlogBoltCreateSerializer(Serializer):
    """Input serializer for creating blogs - no id field."""

    name: Annotated[str, Meta(min_length=1, max_length=255)]
    description: str
    status: BlogStatus = "draft"
    author: int | None = None

    @field_validator("name")
    def validate_name(cls, value: str) -> str:
        return value.strip()

    @field_validator("description")
    def validate_description(cls, value: str) -> str:
        return value.strip()


class BlogBoltUpdateSerializer(Serializer, omit_defaults=True):
    """
    Partial update serializer - all fields optional.
    omit_defaults=True means only provided fields are used.
    """

    name: Annotated[str, Meta(min_length=1, max_length=255)] | None = None
    description: str | None = None
    status: BlogStatus | None = None
    author: int | None = None


# ============================================
# Bolt Serializer CRUD Endpoints
# ============================================

@api.get("/bolt")
async def get_blogs_bolt() -> list[BlogBoltSerializer]:
    """List blogs using Serializer with computed fields."""
    blogs = [blog async for blog in Blog.objects.filter(status="published")[:10]]
    return [
        BlogBoltSerializer(
            id=b.id,
            name=b.name,
            description=b.description,
            status=b.status,
            author=b.author_id,
        )
        for b in blogs
    ]


@api.get("/bolt/{blog_id}")
async def get_blog_bolt(blog_id: int) -> BlogBoltSerializer:
    """Get single blog with full details including computed field."""
    blog = await Blog.objects.aget(id=blog_id)
    return BlogBoltSerializer(
        id=blog.id,
        name=blog.name,
        description=blog.description,
        status=blog.status,
        author=blog.author_id,
    )


@api.post("/bolt")
async def create_blog_bolt(data: BlogBoltCreateSerializer) -> BlogBoltSerializer:
    """Create blog using Serializer - validates input, returns full response."""
    # Use to_dict() to get validated data as dict
    blog = Blog(
        name=data.name,
        description=data.description,
        status=data.status,
        author_id=data.author,
    )
    await blog.asave()

    # Return full serializer with computed fields
    return BlogBoltSerializer(
        id=blog.id,
        name=blog.name,
        description=blog.description,
        status=blog.status,
        author=blog.author_id,
    )


@api.put("/bolt/{blog_id}")
async def update_blog_bolt(blog_id: int, data: BlogBoltCreateSerializer) -> BlogBoltSerializer:
    """Full update using Serializer."""
    blog = await Blog.objects.aget(id=blog_id)

    # Update all fields
    blog.name = data.name
    blog.description = data.description
    blog.status = data.status
    blog.author_id = data.author
    await blog.asave()

    return BlogBoltSerializer(
        id=blog.id,
        name=blog.name,
        description=blog.description,
        status=blog.status,
        author=blog.author_id,
    )


@api.patch("/bolt/{blog_id}")
async def patch_blog_bolt(blog_id: int, data: BlogBoltUpdateSerializer) -> BlogBoltSerializer:
    """Partial update - only update provided fields using update_instance()."""
    blog = await Blog.objects.aget(id=blog_id)

    # Use update_instance() - only updates non-default fields
    # thanks to omit_defaults=True on the serializer
    if data.name is not None:
        blog.name = data.name
    if data.description is not None:
        blog.description = data.description
    if data.status is not None:
        blog.status = data.status
    if data.author is not None:
        blog.author_id = data.author

    await blog.asave()

    return BlogBoltSerializer(
        id=blog.id,
        name=blog.name,
        description=blog.description,
        status=blog.status,
        author=blog.author_id,
    )


@api.delete("/bolt/{blog_id}")
async def delete_blog_bolt(blog_id: int) -> dict:
    """Delete a blog."""
    blog = await Blog.objects.aget(id=blog_id)
    deleted_id = blog.id
    await blog.adelete()
    return {"deleted": True, "id": deleted_id}


@api.get("/{blog_id}")
async def get_blog(blog_id: int) -> BlogSerializer:
    blog = await Blog.objects.select_related("author").aget(id=blog_id)
    return BlogSerializer.from_model(blog)


@api.post("")
async def create_blog(blog: BlogSerializer) -> BlogSerializer:
    """Create a new blog."""
    new_blog = Blog(
        name=blog.name,
        description=blog.description,
        status=blog.status,
        author_id=blog.author,
    )
    await new_blog.asave()
    saved_blog = await Blog.objects.select_related("author").aget(id=new_blog.id)
    return BlogSerializer.from_model(saved_blog)


@api.put("/{blog_id}")
async def update_blog(blog_id: int, data: BlogUpdateSerializer) -> BlogSerializer:
    """Full update - replaces all fields."""
    blog = await Blog.objects.aget(id=blog_id)
    blog.name = data.name
    blog.description = data.description
    blog.status = data.status
    blog.author_id = data.author
    await blog.asave()
    updated_blog = await Blog.objects.select_related("author").aget(id=blog_id)
    return BlogSerializer.from_model(updated_blog)


@api.patch("/{blog_id}")
async def patch_blog(blog_id: int, data: dict) -> BlogSerializer:
    """Partial update - only updates provided fields."""
    blog = await Blog.objects.aget(id=blog_id)

    allowed_fields = {"name", "description", "status"}
    for field, value in data.items():
        if field in allowed_fields:
            setattr(blog, field, value)
        elif field == "author":
            blog.author_id = value

    await blog.asave()
    patched_blog = await Blog.objects.select_related("author").aget(id=blog_id)
    return BlogSerializer.from_model(patched_blog)


@api.delete("/{blog_id}")
async def delete_blog(blog_id: int) -> dict:
    """Delete a blog."""
    blog = await Blog.objects.aget(id=blog_id)
    blog_id_deleted = blog.id
    await blog.adelete()
    return {"deleted": True, "id": blog_id_deleted}


# Author endpoints (nested under /blogs/authors)
@api.get("/authors")
async def get_authors() -> list[AuthorSerializer]:
    return [author async for author in Author.objects.all()]


@api.get("/authors/{author_id}")
async def get_author(author_id: int) -> AuthorSerializer:
    return await Author.objects.aget(id=author_id)


@api.post("/authors")
async def create_author(author: AuthorSerializer) -> AuthorSerializer:
    new_author = Author(
        name=author.name,
        email=author.email,
        bio=author.bio,
    )
    await new_author.asave()
    return new_author


@api.put("/authors/{author_id}")
async def update_author(author_id: int, data: AuthorUpdateSerializer) -> AuthorSerializer:
    """Full update - replaces all fields."""
    author = await Author.objects.aget(id=author_id)
    author.name = data.name
    author.email = data.email
    author.bio = data.bio
    await author.asave()
    return author


@api.patch("/authors/{author_id}")
async def patch_author(author_id: int, data: dict) -> AuthorSerializer:
    """Partial update - only updates provided fields."""
    author = await Author.objects.aget(id=author_id)

    allowed_fields = {"name", "email", "bio"}
    for field, value in data.items():
        if field in allowed_fields:
            setattr(author, field, value)

    await author.asave()
    return author


@api.delete("/authors/{author_id}")
async def delete_author(author_id: int) -> dict:
    """Delete an author."""
    author = await Author.objects.aget(id=author_id)
    author_id_deleted = author.id
    await author.adelete()
    return {"deleted": True, "id": author_id_deleted}


# Seed endpoint
@api.get("/seed")
async def seed_authors_and_blogs(authors: int = 5, blogs_per_author: int = 3) -> SeedResult:
    """
    Auto-generate fake authors and blogs.

    Query params:
        authors: Number of authors to create (default: 5)
        blogs_per_author: Number of blogs per author (default: 3)

    Example: GET /seed?authors=10&blogs_per_author=5
    """
    first_names = ["John", "Jane", "Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", "Grace", "Henry"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Wilson", "Taylor"]
    topics = ["Technology", "Science", "Travel", "Food", "Health", "Finance", "Sports", "Entertainment", "Politics", "Art"]
    adjectives = ["Amazing", "Ultimate", "Essential", "Complete", "Practical", "Modern", "Advanced", "Simple", "Expert", "Beginner"]
    bios = [
        "A passionate writer with years of experience.",
        "Tech enthusiast and avid blogger.",
        "Loves exploring new ideas and sharing knowledge.",
        "Professional content creator and storyteller.",
        "Dedicated to making complex topics simple.",
    ]

    authors_created = 0
    blogs_created = 0

    for _ in range(authors):
        first = random.choice(first_names)
        last = random.choice(last_names)
        unique_id = uuid.uuid4().hex[:6]

        author = Author(
            name=f"{first} {last}",
            email=f"{first.lower()}.{last.lower()}.{unique_id}@example.com",
            bio=random.choice(bios),
        )
        await author.asave()
        authors_created += 1

        for _ in range(blogs_per_author):
            topic = random.choice(topics)
            adj = random.choice(adjectives)
            status = random.choice(["published", "draft"])

            blog = Blog(
                name=f"The {adj} {topic} Blog",
                description=f"A blog about {topic.lower()} covering various aspects and insights.",
                status=status,
                author=author,
            )
            await blog.asave()
            blogs_created += 1

    return SeedResult(
        authors_created=authors_created,
        blogs_created=blogs_created,
        message=f"Successfully created {authors_created} authors and {blogs_created} blogs",
    )
