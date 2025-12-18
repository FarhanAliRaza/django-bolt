# Nested Serializers

Django-Bolt supports nested serializers for validating related objects. This guide shows how to handle foreign keys, many-to-many relationships, and JSON fields with type-safe nested validation.

## Overview

Nested serializers allow you to:
- Validate related objects with full type safety
- Accept either complete nested objects OR just IDs (for lazy-loaded relationships)
- Handle both single relationships (ForeignKey) and collections (ManyToMany)
- Combine nested validation with custom field validators

## Basic Syntax

### Single Nested Object (ForeignKey)

```python
from typing import Annotated
from django_bolt.serializers import Serializer, Nested

class AuthorSerializer(Serializer):
    id: int
    name: str
    email: str

class BookSerializer(Serializer):
    title: str
    isbn: str
    # Can accept either an AuthorSerializer or just an int ID
    author: Annotated[AuthorSerializer | int, Nested(AuthorSerializer)]

# Usage with nested object
book_data = {
    "title": "Django for Beginners",
    "isbn": "978-0-123456-78-9",
    "author": {
        "id": 1,
        "name": "John Smith",
        "email": "john@example.com"
    }
}
book = BookSerializer(**book_data)
assert isinstance(book.author, AuthorSerializer)
assert book.author.name == "John Smith"

# Usage with ID (when not using select_related)
book_data2 = {
    "title": "Advanced Django",
    "isbn": "978-0-987654-32-1",
    "author": 42  # Just the ID
}
book2 = BookSerializer(**book_data2)
assert book2.author == 42  # Stays as ID
```

### Many-to-Many Relationships

```python
class TagSerializer(Serializer):
    id: int
    name: str

class BlogPostSerializer(Serializer):
    title: str
    content: str
    # Can accept list of TagSerializers or list of IDs
    tags: Annotated[list[TagSerializer] | list[int], Nested(TagSerializer, many=True)]

# Usage with nested objects
post = BlogPostSerializer(
    title="Getting Started with Serializers",
    content="...",
    tags=[
        {"id": 1, "name": "django"},
        {"id": 2, "name": "serialization"},
    ]
)
assert all(isinstance(t, TagSerializer) for t in post.tags)

# Usage with IDs
post2 = BlogPostSerializer(
    title="Advanced Topics",
    content="...",
    tags=[1, 2, 3]  # Just IDs
)
assert post2.tags == [1, 2, 3]

# Mixed usage
post3 = BlogPostSerializer(
    title="Mixed Example",
    content="...",
    tags=[
        1,
        {"id": 2, "name": "python"},
        3
    ]
)
assert isinstance(post3.tags[1], TagSerializer)
assert post3.tags[0] == 1
```

## Configuration Options

### `allow_id_fallback` Parameter

By default, nested fields accept IDs as a fallback (for unselected relationships). You can disable this:

```python
class StrictBookSerializer(Serializer):
    title: str
    # Must always be a full AuthorSerializer object
    author: Annotated[
        AuthorSerializer,
        Nested(AuthorSerializer, allow_id_fallback=False)
    ]

# This will raise an error
book = StrictBookSerializer(
    title="Test",
    author=1  # Error: expected AuthorSerializer, not ID
)
```

### `many` Parameter

Use `many=True` for list relationships:

```python
# Single object
single: Annotated[AuthorSerializer | int, Nested(AuthorSerializer)]

# List of objects
multiple: Annotated[
    list[AuthorSerializer] | list[int],
    Nested(AuthorSerializer, many=True)
]
```

## API Patterns

### Pattern 1: List with IDs (No Prefetch)

```python
@api.get("/posts")
async def list_posts():
    # Simple query without prefetch_related
    posts = await Post.objects.all()
    return [BlogPostSerializer.from_model(p) for p in posts]
    # Result: tags: [1, 2, 3]
```

### Pattern 2: Detailed List (With Prefetch)

```python
@api.get("/posts/detailed")
async def list_posts_detailed():
    # Query with prefetch_related
    posts = await Post.objects.prefetch_related('tags').all()
    return [BlogPostSerializer.from_model(p) for p in posts]
    # Result: tags: [TagSerializer(...), TagSerializer(...), ...]
```

### Pattern 3: Create with Full Objects

```python
class BlogPostCreateSerializer(Serializer):
    title: str
    content: str
    tags: Annotated[list[TagSerializer], Nested(TagSerializer, many=True, allow_id_fallback=False)]

@api.post("/posts", response_model=BlogPostSerializer)
async def create_post(data: BlogPostCreateSerializer):
    # Requires full tag objects
    post = await Post.objects.acreate(
        title=data.title,
        content=data.content
    )
    # Add tags from serializer data
    for tag in data.tags:
        await post.tags.aadd(tag.id)  # Extract ID from serializer
    return BlogPostSerializer.from_model(post)
```

## Validation in Nested Objects

Field validators work at every level:

```python
class CommentSerializer(Serializer):
    id: int
    text: str

    @field_validator('text')
    def validate_text(cls, value):
        if len(value) < 5:
            raise ValueError("Comment must be at least 5 characters")
        return value

class PostSerializer(Serializer):
    title: str
    comments: Annotated[
        list[CommentSerializer],
        Nested(CommentSerializer, many=True)
    ]

# Each comment in the list will be validated
post = PostSerializer(
    title="Test",
    comments=[
        {"id": 1, "text": "Great post!"},  # OK
        {"id": 2, "text": "X"},  # Error: too short
    ]
)  # Raises ValidationError
```

## JSONField Integration

For JSONField, use nested serializers to validate structure:

```python
from django.db import models

class Article(models.Model):
    title = models.CharField(max_length=200)
    metadata = models.JSONField()  # Stores structured data

class MetadataSerializer(Serializer):
    author: str
    keywords: list[str]
    published_date: str

class ArticleSerializer(Serializer):
    title: str
    # Validate the JSON structure
    metadata: Annotated[MetadataSerializer, Nested(MetadataSerializer)]

# Usage
article = ArticleSerializer(
    title="Article",
    metadata={
        "author": "Jane Doe",
        "keywords": ["python", "django"],
        "published_date": "2024-11-15"
    }
)
assert isinstance(article.metadata, MetadataSerializer)
```

## Error Handling

Nested validation errors include field context:

```python
class AuthorSerializer(Serializer):
    id: int
    name: str

class BookSerializer(Serializer):
    title: str
    author: Annotated[AuthorSerializer | int, Nested(AuthorSerializer)]

try:
    book = BookSerializer(
        title="Test",
        author={
            "id": "not_an_int",  # Wrong type
            "name": "John"
        }
    )
except ValidationError as e:
    # Error message includes field path: "author: ..."
    print(e)
```

## Best Practices

### 1. Use Type Unions for Flexibility

```python
# Good: Supports both IDs and objects
author: Annotated[AuthorSerializer | int, Nested(AuthorSerializer)]

# Less flexible: Always requires objects
author: Annotated[AuthorSerializer, Nested(AuthorSerializer, allow_id_fallback=False)]
```

### 2. Choose Query Strategy Based on Response

```python
# If returning IDs:
posts = await Post.objects.all()
return {"tags": [1, 2, 3]}

# If returning objects:
posts = await Post.objects.prefetch_related('tags').all()
return {"tags": [{"id": 1, "name": "django"}, ...]}
```

### 3. Separate Create/Update/Read Serializers

```python
# For accepting input (with full objects)
class CommentCreateSerializer(Serializer):
    text: str
    author: Annotated[UserSerializer, Nested(UserSerializer, allow_id_fallback=False)]

# For returning data (can be IDs or objects)
class CommentPublicSerializer(Serializer):
    id: int
    text: str
    author: Annotated[UserSerializer | int, Nested(UserSerializer)]
```

### 4. Combine with Field Validators

```python
class RelationshipSerializer(Serializer):
    author: Annotated[AuthorSerializer | int, Nested(AuthorSerializer)]

    @field_validator('author')
    def validate_author_not_self(cls, value):
        # Only run custom validation after nested validation
        if isinstance(value, AuthorSerializer):
            # Check business logic on the serializer
            if value.id == 0:
                raise ValueError("Cannot author your own post")
        return value
```

## Examples

### Blog with Comments and Authors

```python
class UserSerializer(Serializer):
    id: int
    username: str
    email: str

class CommentSerializer(Serializer):
    id: int
    text: str
    author: Annotated[UserSerializer | int, Nested(UserSerializer)]

class BlogPostSerializer(Serializer):
    id: int
    title: str
    content: str
    author: Annotated[UserSerializer | int, Nested(UserSerializer)]
    comments: Annotated[
        list[CommentSerializer] | list[int],
        Nested(CommentSerializer, many=True)
    ]

@api.get("/posts/{post_id}")
async def get_post(post_id: int):
    # With select_related and prefetch_related
    post = await (
        Post.objects
        .select_related('author')
        .prefetch_related('comments__author')
        .aget(id=post_id)
    )
    return BlogPostSerializer.from_model(post)
    # Returns full nested objects

@api.get("/posts")
async def list_posts():
    # Without prefetch
    posts = await Post.objects.all()
    return [BlogPostSerializer.from_model(p) for p in posts]
    # Returns IDs only
```

## Testing

```python
def test_nested_with_dict():
    """Test nested serializer accepts dict input."""
    author_data = {"id": 1, "name": "Alice"}
    serializer = BookSerializer(
        title="Test",
        author=author_data
    )
    assert isinstance(serializer.author, AuthorSerializer)

def test_nested_with_id():
    """Test nested serializer accepts ID fallback."""
    serializer = BookSerializer(
        title="Test",
        author=1  # ID only
    )
    assert serializer.author == 1

def test_nested_many():
    """Test nested many-to-many."""
    serializer = BlogPostSerializer(
        title="Test",
        content="...",
        tags=[1, 2, 3]
    )
    assert serializer.tags == [1, 2, 3]
```

## See Also

- [Serializers Documentation](./SERIALIZERS.md)
- [Field Validators Documentation](./SERIALIZERS.md#field-validators)
- [Model Integration](./SERIALIZERS.md#django-model-integration)
