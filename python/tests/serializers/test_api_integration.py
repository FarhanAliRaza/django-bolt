"""
Integration tests for nested serializers with sync views and TestClient.

This test suite demonstrates 4 different API endpoints that use nested serializers:
1. Simple nested ForeignKey (Author in BlogPost)
2. Many-to-many nested relationships (Tags in BlogPost)
3. Deeply nested structures (Comments with Authors in BlogPost)
4. Mixed nested relationships with validation

These tests use TestClient to make real HTTP requests and verify the full
request/response cycle with nested serializers.
"""

from __future__ import annotations

import json
from typing import Annotated

import pytest
from asgiref.sync import sync_to_async
from msgspec import Meta

from django_bolt.api import BoltAPI
from django_bolt.serializers import Nested, Serializer, field_validator
from django_bolt.testing import TestClient
from tests.test_models import Author, BlogPost, Comment, Tag


# ============================================================================
# SERIALIZERS - Define all serializers for nested relationships
# ============================================================================


class AuthorSerializer(Serializer):
    """Serializer for Author model with email validation."""

    id: int
    # Use Meta(min_length=2) for declarative validation
    name: Annotated[str, Meta(min_length=2)]
    # Use Meta(pattern=...) for email validation
    email: Annotated[str, Meta(pattern=r"^[^@]+@[^@]+\.[^@]+$")]
    bio: str = ""

    @field_validator("name")
    def strip_name(cls, value: str) -> str:
        """Strip whitespace from name."""
        return value.strip()

    @field_validator("email")
    def lowercase_email(cls, value: str) -> str:
        """Convert email to lowercase."""
        return value.lower()


class TagSerializer(Serializer):
    """Serializer for Tag model."""

    id: int
    name: str
    description: str = ""


class CommentSerializer(Serializer):
    """Serializer for Comment model with nested author."""

    id: int
    text: str
    # Author as full object
    author: Annotated[AuthorSerializer, Nested(AuthorSerializer)]


class BlogPostSerializer(Serializer):
    """Serializer for BlogPost with nested author and tags - OUTPUT ONLY."""

    id: int
    title: str
    content: str
    # Author relationship - full object required
    author: Annotated[AuthorSerializer, Nested(AuthorSerializer)]
    # Tags relationship - full objects required
    tags: Annotated[list[TagSerializer], Nested(TagSerializer, many=True)]
    published: bool = False


class BlogPostInputSerializer(Serializer):
    """Serializer for BlogPost input (CREATE/UPDATE) - accepts nested objects only."""

    title: str
    content: str
    # For input, we accept full nested objects (msgspec can decode these)
    author: Annotated[AuthorSerializer, Nested(AuthorSerializer)]
    tags: Annotated[list[TagSerializer], Nested(TagSerializer, many=True)]
    published: bool = False


class BlogPostDetailedSerializer(Serializer):
    """Serializer for BlogPost with nested comments - OUTPUT ONLY."""

    id: int
    title: str
    content: str
    author: Annotated[AuthorSerializer, Nested(AuthorSerializer)]
    tags: Annotated[list[TagSerializer], Nested(TagSerializer, many=True)]
    # Comments nested with their own nested authors
    comments: Annotated[list[CommentSerializer], Nested(CommentSerializer, many=True)]
    published: bool = False


class BlogPostDetailedInputSerializer(Serializer):
    """Serializer for BlogPost with nested comments - INPUT for CREATE."""

    title: str
    content: str
    author: Annotated[AuthorSerializer, Nested(AuthorSerializer)]
    tags: Annotated[list[TagSerializer], Nested(TagSerializer, many=True)]
    # Comments nested with their own nested authors
    comments: Annotated[list[CommentSerializer], Nested(CommentSerializer, many=True)]
    published: bool = False


# ============================================================================
# API 1: Simple Nested ForeignKey
# ============================================================================


api_1_nested_fk = BoltAPI()


@api_1_nested_fk.get("/posts/{post_id}")
def get_post_simple(post_id: int):
    """
    API 1: Get a single post with its nested author.

    Query with select_related to include the author as a nested object.
    If author is not loaded, it returns just the ID.
    """
    post = BlogPost.objects.select_related("author").get(id=post_id)
    return BlogPostSerializer.from_model(post)


@api_1_nested_fk.post("/posts")
def create_post_simple(data: BlogPostInputSerializer):
    """
    API 1: Create a new post with author reference.

    Accepts nested author (must be full object for input).
    """
    author_id = data.author.id
    post = BlogPost.objects.create(
        title=data.title,
        content=data.content,
        author_id=author_id,
        published=data.published,
    )
    return BlogPostSerializer.from_model(post)


# ============================================================================
# API 2: Many-to-Many Nested Relationships
# ============================================================================


api_2_nested_m2m = BoltAPI()


@api_2_nested_m2m.get("/posts/{post_id}/detailed")
def get_post_with_tags(post_id: int):
    """
    API 2: Get a post with author and tags as nested objects.

    Uses prefetch_related to load tags efficiently.
    """
    post = (
        BlogPost.objects.select_related("author")
        .prefetch_related("tags")
        .get(id=post_id)
    )
    return BlogPostSerializer.from_model(post)


@api_2_nested_m2m.post("/posts/with-tags")
def create_post_with_tags(data: BlogPostInputSerializer):
    """
    API 2: Create a post with author and tags.

    Accepts both author and tags as full nested objects.
    """
    author_id = data.author.id

    post = BlogPost.objects.create(
        title=data.title,
        content=data.content,
        author_id=author_id,
        published=data.published,
    )

    # Add tags
    tag_ids = [tag.id for tag in data.tags]
    if tag_ids:
        post.tags.set(tag_ids)

    return BlogPostSerializer.from_model(post)


# ============================================================================
# API 3: Deeply Nested Structures (Nested within Nested)
# ============================================================================


api_3_deeply_nested = BoltAPI()


@api_3_deeply_nested.get("/posts/{post_id}/full")
def get_post_full(post_id: int):
    """
    API 3: Get a post with all relationships fully populated.

    Includes author, tags, and comments with their authors.
    This demonstrates deeply nested structures (comments -> authors).
    """
    post = (
        BlogPost.objects
        .select_related("author")
        .prefetch_related("tags", "comments__author")
        .get(id=post_id)
    )
    return BlogPostDetailedSerializer.from_model(post)


@api_3_deeply_nested.post("/posts/full")
def create_post_full(data: BlogPostDetailedInputSerializer):
    """
    API 3: Create a post with full nested structure.

    Accepts author, tags, and comments (each with their own nested authors).
    """
    # Extract author ID
    author_id = data.author.id

    # Create post
    post = BlogPost.objects.create(
        title=data.title,
        content=data.content,
        author_id=author_id,
        published=data.published,
    )

    # Add tags
    tag_ids = [tag.id for tag in data.tags]
    if tag_ids:
        post.tags.set(tag_ids)

    # Add comments
    for comment_data in data.comments:
        comment_author_id = comment_data.author.id if isinstance(comment_data.author, AuthorSerializer) else comment_data.author

        Comment.objects.create(
            post=post,
            author_id=comment_author_id,
            text=comment_data.text,
        )

    return BlogPostDetailedSerializer.from_model(post)


# ============================================================================
# API 4: Mixed Nested with Validation
# ============================================================================


class BlogPostCreateSerializer(Serializer):
    """Stricter serializer for creating posts - author and tags must be full objects."""

    # Use Meta(min_length=...) for declarative validation
    title: Annotated[str, Meta(min_length=3)]
    content: Annotated[str, Meta(min_length=10)]
    # Author must be a full object, not just ID
    author: Annotated[AuthorSerializer, Nested(AuthorSerializer)]
    # Tags must be full objects for input
    tags: Annotated[list[TagSerializer], Nested(TagSerializer, many=True)]
    published: bool = False

    @field_validator("title")
    def strip_title(cls, value: str) -> str:
        """Strip whitespace from title."""
        return value.strip()

    @field_validator("content")
    def strip_content(cls, value: str) -> str:
        """Strip whitespace from content."""
        return value.strip()


api_4_mixed_validation = BoltAPI()


@api_4_mixed_validation.post("/posts/strict")
def create_post_strict(data: BlogPostCreateSerializer):
    """
    API 4: Create a post with strict validation.

    - Author must be a full AuthorSerializer (not just ID)
    - Tags must be full TagSerializers (not just IDs)
    - Title and content are validated for minimum length
    - Author validation (email, name) is enforced
    """
    # At this point, data.author is guaranteed to be an AuthorSerializer
    # and data.tags is guaranteed to be list[TagSerializer]
    # because allow_id_fallback=False

    # Create post
    post = BlogPost.objects.create(
        title=data.title,
        content=data.content,
        author_id=data.author.id,
        published=data.published,
    )

    # Add tags
    tag_ids = [tag.id for tag in data.tags]
    if tag_ids:
        post.tags.set(tag_ids)

    return BlogPostSerializer.from_model(post)


@api_4_mixed_validation.get("/posts/{post_id}/validate")
def get_post_and_validate(post_id: int):
    """
    API 4: Get a post and validate the response structure.

    Demonstrates that the response is properly serialized and can be
    re-validated through the same serializer.
    """
    post = (
        BlogPost.objects.select_related("author")
        .prefetch_related("tags")
        .get(id=post_id)
    )

    # Get the response data
    response_data = BlogPostSerializer.from_model(post)

    # Validate that it can be re-serialized
    # This ensures type safety and structure consistency
    validated = BlogPostSerializer(
        id=response_data.id,
        title=response_data.title,
        content=response_data.content,
        author=response_data.author,
        tags=response_data.tags,
        published=response_data.published,
    )

    return validated


# ============================================================================
# PYTEST FIXTURES - TestClient instances for each API
# ============================================================================


@pytest.fixture
def client_api_1():
    """TestClient for API 1: Simple nested ForeignKey."""
    return TestClient(api_1_nested_fk)


@pytest.fixture
def client_api_2():
    """TestClient for API 2: Many-to-many nested relationships."""
    return TestClient(api_2_nested_m2m)


@pytest.fixture
def client_api_3():
    """TestClient for API 3: Deeply nested structures."""
    return TestClient(api_3_deeply_nested)


@pytest.fixture
def client_api_4():
    """TestClient for API 4: Mixed nested with validation."""
    return TestClient(api_4_mixed_validation)


# ============================================================================
# TESTS - Using TestClient for HTTP request/response testing
# ============================================================================


class TestAPI1SimpleNestedFK:
    """Test API 1: Simple nested ForeignKey relationships."""

    @pytest.mark.django_db(transaction=True)
    def test_get_post_with_select_related(self, client_api_1):
        """Test getting a post with author loaded via select_related."""
        # Create test data
        author = Author.objects.create(name="Alice", email="alice@example.com")
        post = BlogPost.objects.create(
            title="Test Post", content="This is test content", author=author
        )

        # Make HTTP request
        response = client_api_1.get(f"/posts/{post.id}")

        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Test Post"
        assert data["id"] == post.id
        # Author should be either ID or nested object
        if isinstance(data["author"], dict):
            assert data["author"]["name"] == "Alice"
        else:
            assert data["author"] == author.id

    @pytest.mark.django_db(transaction=True)
    def test_create_post_with_author_dict(self, client_api_1):
        """Test creating a post with author as nested dict via POST."""
        # Create author first
        author = Author.objects.create(name="Bob", email="bob@example.com")

        # Send POST request with nested author dict
        payload = {
            "title": "New Post",
            "content": "New post content here",
            "author": {"id": author.id, "name": "Bob", "email": "bob@example.com"},
            "tags": [],
            "published": False,
        }
        response = client_api_1.post("/posts", json=payload)

        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "New Post"
        assert BlogPost.objects.filter(title="New Post").exists()

    @pytest.mark.django_db(transaction=True)
    def test_create_post_with_author_id(self, client_api_1):
        """Test creating a post with author as nested object."""
        # Create author first
        author = Author.objects.create(name="Charlie", email="charlie@example.com")

        # Send POST request with full author object (required by input serializer)
        payload = {
            "title": "Simple Post",
            "content": "Simple post content",
            "author": {"id": author.id, "name": "Charlie", "email": "charlie@example.com"},
            "tags": [],
            "published": False,
        }
        response = client_api_1.post("/posts", json=payload)

        # Verify response and database
        assert response.status_code == 200
        created_post = BlogPost.objects.get(title="Simple Post")
        assert created_post.author_id == author.id


class TestAPI2NestedM2M:
    """Test API 2: Many-to-many nested relationships."""

    @pytest.mark.django_db(transaction=True)
    def test_get_post_with_tags_prefetch(self, client_api_2):
        """Test getting a post with tags loaded via prefetch_related."""
        # Create test data
        author = Author.objects.create(name="Dave", email="dave@example.com")
        post = BlogPost.objects.create(
            title="Tagged Post", content="Post content", author=author
        )

        # Create and add tags
        tag1 = Tag.objects.create(name="python")
        tag2 = Tag.objects.create(name="django")
        post.tags.add(tag1, tag2)

        # Make HTTP request
        response = client_api_2.get(f"/posts/{post.id}/detailed")

        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Tagged Post"
        assert len(data["tags"]) == 2
        # Tags should be either IDs or nested objects
        for tag in data["tags"]:
            assert isinstance(tag, (int, dict))

    @pytest.mark.django_db(transaction=True)
    def test_create_post_with_tags_dicts(self, client_api_2):
        """Test creating a post with tags as nested dicts."""
        # Create author
        author = Author.objects.create(name="Eve", email="eve@example.com")

        # Create tags first
        tag1 = Tag.objects.create(name="testing")
        tag2 = Tag.objects.create(name="integration")

        # Send POST request with nested tag dicts and full author
        payload = {
            "title": "Post with Tags",
            "content": "Content with tags",
            "author": {"id": author.id, "name": "Eve", "email": "eve@example.com"},
            "tags": [
                {"id": tag1.id, "name": "testing"},
                {"id": tag2.id, "name": "integration"},
            ],
            "published": True,
        }
        response = client_api_2.post("/posts/with-tags", json=payload)

        # Verify response and database
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Post with Tags"
        created_post = BlogPost.objects.get(title="Post with Tags")
        assert created_post.tags.count() == 2
        assert created_post.published is True

    @pytest.mark.django_db(transaction=True)
    def test_create_post_with_tags_ids(self, client_api_2):
        """Test creating a post with tags as nested objects."""
        # Create author
        author = Author.objects.create(name="Frank", email="frank@example.com")

        # Create tags
        tag1 = Tag.objects.create(name="tag1")
        tag2 = Tag.objects.create(name="tag2")

        # Send POST request with full tag objects (required by input serializer)
        payload = {
            "title": "Post with Tag IDs",
            "content": "Content with tag IDs",
            "author": {"id": author.id, "name": "Frank", "email": "frank@example.com"},
            "tags": [
                {"id": tag1.id, "name": "tag1"},
                {"id": tag2.id, "name": "tag2"},
            ],
            "published": False,
        }
        response = client_api_2.post("/posts/with-tags", json=payload)

        # Verify response and database
        assert response.status_code == 200
        created_post = BlogPost.objects.get(title="Post with Tag IDs")
        assert created_post.tags.count() == 2


class TestAPI3DeeplyNested:
    """Test API 3: Deeply nested structures (nested within nested)."""

    @pytest.mark.django_db(transaction=True)
    def test_get_post_full_with_comments_and_authors(self, client_api_3):
        """Test getting a post with all relationships including nested comments."""
        # Create authors
        post_author = Author.objects.create(name="Grace", email="grace@example.com")
        commenter = Author.objects.create(name="Henry", email="henry@example.com")

        # Create post with tags
        post = BlogPost.objects.create(
            title="Complex Post", content="Complex post content", author=post_author
        )

        tag = Tag.objects.create(name="complex")
        post.tags.add(tag)

        # Create comments
        comment1 = Comment.objects.create(
            post=post, author=commenter, text="Great post!"
        )

        # Make HTTP request
        response = client_api_3.get(f"/posts/{post.id}/full")

        # Verify response structure
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Complex Post"

        # Author should be nested
        if isinstance(data["author"], dict):
            assert data["author"]["name"] == "Grace"

        # Tags should be present
        assert len(data["tags"]) > 0

        # Comments should be nested with authors
        assert len(data["comments"]) > 0
        first_comment = data["comments"][0]
        if isinstance(first_comment, dict):
            assert first_comment["text"] == "Great post!"
            if isinstance(first_comment["author"], dict):
                assert first_comment["author"]["name"] == "Henry"

    @pytest.mark.django_db(transaction=True)
    def test_create_post_full_with_nested_comments(self, client_api_3):
        """Test creating a post with full nested structure including comments."""
        # Create authors in DB first
        post_author = Author.objects.create(name="Iris", email="iris@example.com")
        commenter = Author.objects.create(name="Jack", email="jack@example.com")

        # Create tag
        tag = Tag.objects.create(name="nested")

        # Send POST request with full nesting
        payload = {
            "title": "Full Post",
            "content": "Full post with nested comments",
            "author": {"id": post_author.id, "name": "Iris", "email": "iris@example.com"},
            "tags": [{"id": tag.id, "name": "nested"}],
            "comments": [
                {
                    "id": 0,
                    "text": "Nested comment 1",
                    "author": {"id": commenter.id, "name": "Jack", "email": "jack@example.com"},
                },
                {
                    "id": 0,
                    "text": "Nested comment 2",
                    "author": {"id": commenter.id, "name": "Jack", "email": "jack@example.com"},
                },
            ],
            "published": True,
        }
        response = client_api_3.post("/posts/full", json=payload)

        # Verify response and database
        assert response.status_code == 200
        created_post = BlogPost.objects.get(title="Full Post")
        assert created_post.author_id == post_author.id
        assert created_post.tags.count() == 1
        assert created_post.comments.count() == 2


class TestAPI4MixedValidation:
    """Test API 4: Mixed nested with validation."""

    @pytest.mark.django_db(transaction=True)
    def test_create_post_strict_with_full_author(self, client_api_4):
        """Test creating a post with strict validation and full author object."""
        # Create author
        author = Author.objects.create(name="Kate", email="kate@example.com")

        # Send POST request with full author (required by strict validation)
        payload = {
            "title": "Strict Post",
            "content": "This is a strict post with full author object",
            "author": {"id": author.id, "name": "Kate", "email": "kate@example.com"},
            "tags": [],
            "published": True,
        }
        response = client_api_4.post("/posts/strict", json=payload)

        # Verify response and database
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Strict Post"
        created_post = BlogPost.objects.get(title="Strict Post")
        assert created_post.author_id == author.id
        assert created_post.published is True

    @pytest.mark.django_db(transaction=True)
    def test_create_post_strict_validation_fails_without_author_object(self, client_api_4):
        """Test that strict validation fails if author is just an ID."""
        # Create author
        author = Author.objects.create(name="Liam", email="liam@example.com")

        # Send POST request with just author ID (should fail)
        payload = {
            "title": "Should Fail",
            "content": "This should fail because author is just ID",
            "author": author.id,  # Just ID - not allowed
            "tags": [],
            "published": False,
        }
        response = client_api_4.post("/posts/strict", json=payload)

        # Verify request fails
        assert response.status_code == 400 or response.status_code == 422

    @pytest.mark.django_db(transaction=True)
    def test_create_post_strict_title_validation(self, client_api_4):
        """Test that title validation is enforced."""
        author = Author.objects.create(name="Mia", email="mia@example.com")

        # Send POST request with short title (should fail)
        payload = {
            "title": "Hi",  # Too short
            "content": "This content is long enough but title is not",
            "author": {"id": author.id, "name": "Mia", "email": "mia@example.com"},
            "tags": [],
            "published": False,
        }
        response = client_api_4.post("/posts/strict", json=payload)

        # Verify request fails
        assert response.status_code == 400 or response.status_code == 422

    @pytest.mark.django_db(transaction=True)
    def test_create_post_strict_content_validation(self, client_api_4):
        """Test that content validation is enforced."""
        author = Author.objects.create(name="Noah", email="noah@example.com")

        # Send POST request with short content (should fail)
        payload = {
            "title": "Valid Title",
            "content": "Short",  # Too short
            "author": {"id": author.id, "name": "Noah", "email": "noah@example.com"},
            "tags": [],
            "published": False,
        }
        response = client_api_4.post("/posts/strict", json=payload)

        # Verify request fails
        assert response.status_code == 400 or response.status_code == 422

    @pytest.mark.django_db(transaction=True)
    def test_create_post_strict_author_email_validation(self, client_api_4):
        """Test that author email validation is enforced in nested object."""
        # Send POST request with invalid author email
        payload = {
            "title": "Valid Title",
            "content": "This is valid content for the post",
            "author": {"id": 1, "name": "Invalid", "email": "invalidemail"},
            "tags": [],
            "published": False,
        }
        response = client_api_4.post("/posts/strict", json=payload)

        # Verify request fails
        assert response.status_code == 400 or response.status_code == 422

    @pytest.mark.django_db(transaction=True)
    def test_get_post_and_validate_roundtrip(self, client_api_4):
        """Test that response can be re-validated through the serializer."""
        # Create test data
        author = Author.objects.create(name="Olivia", email="olivia@example.com")
        post = BlogPost.objects.create(
            title="Roundtrip Post", content="Testing roundtrip validation", author=author
        )

        tag = Tag.objects.create(name="roundtrip")
        post.tags.add(tag)

        # Make HTTP request
        response = client_api_4.get(f"/posts/{post.id}/validate")

        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Roundtrip Post"
        assert data["id"] == post.id
