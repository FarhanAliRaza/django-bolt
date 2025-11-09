"""
Complete example of msgspec ModelSerializer with Django ORM.

Demonstrates:
- ORM read operations
- ORM write operations
- Custom validators
- Computed fields
- Nested serializers
"""
from django_bolt import BoltAPI, ModelSerializer, Serializer
from django.db import models
from typing import List, Optional


# ============================================================
# 1. Define Django Models
# ============================================================

class Author(models.Model):
    """Author model."""
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'example'


class Book(models.Model):
    """Book model with foreign key to Author."""
    title = models.CharField(max_length=200)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='books')
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    pages = models.IntegerField()
    published_date = models.DateField()
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'example'


# ============================================================
# 2. Define Serializers with Validators & Computed Fields
# ============================================================

# Simple Author Serializer (for nesting)
class AuthorSummarySerializer(Serializer):
    """Minimal author info for nested use."""
    id: int
    name: str
    email: str


# Full Author Serializer with computed field
@ModelSerializer
class AuthorSerializer:
    """Author serializer with validation and computed fields."""

    class Meta:
        model = Author
        fields = ['id', 'name', 'email', 'bio', 'book_count', 'created_at']
        read_only_fields = ['id', 'created_at', 'book_count']

    # Custom validator for email
    def validate_email(self, value: str) -> str:
        """Ensure email is from allowed domain."""
        if not value.endswith(('@example.com', '@publisher.com')):
            raise ValueError("Email must be from example.com or publisher.com")
        return value

    # Custom validator for name
    def validate_name(self, value: str) -> str:
        """Ensure name is not empty and properly formatted."""
        if len(value.strip()) < 2:
            raise ValueError("Name must be at least 2 characters")
        return value.strip().title()

    # Computed field - count of books
    @staticmethod
    def get_book_count(obj) -> int:
        """Calculate number of books by this author."""
        return obj.books.count()


# Book Serializer with nested author and computed fields
@ModelSerializer
class BookSerializer:
    """Book serializer with nested author, validators, and computed fields."""

    class Meta:
        model = Book
        fields = [
            'id', 'title', 'description', 'price', 'pages',
            'published_date', 'is_published', 'author_id',
            'author', 'price_category', 'reading_time', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'price_category', 'reading_time']

    # Nested serializer - author details
    author: Optional[AuthorSummarySerializer] = None

    # Custom validators
    def validate_price(self, value: float) -> float:
        """Ensure price is positive and reasonable."""
        if value <= 0:
            raise ValueError("Price must be positive")
        if value > 1000:
            raise ValueError("Price seems too high (max $1000)")
        return value

    def validate_pages(self, value: int) -> int:
        """Ensure page count is reasonable."""
        if value < 1:
            raise ValueError("Book must have at least 1 page")
        if value > 10000:
            raise ValueError("Page count seems unrealistic")
        return value

    def validate_title(self, value: str) -> str:
        """Ensure title is not empty."""
        if len(value.strip()) < 3:
            raise ValueError("Title must be at least 3 characters")
        return value.strip()

    # Computed field - price category
    @staticmethod
    def get_price_category(obj) -> str:
        """Categorize book by price."""
        price = float(obj.price)
        if price < 10:
            return "budget"
        elif price < 30:
            return "standard"
        else:
            return "premium"

    # Computed field - estimated reading time
    def get_reading_time(obj) -> str:
        """Estimate reading time based on pages (250 words/page, 200 wpm)."""
        minutes = (obj.pages * 250) / 200
        hours = minutes / 60
        if hours < 1:
            return f"{int(minutes)} minutes"
        elif hours < 2:
            return f"{hours:.1f} hour"
        else:
            return f"{hours:.1f} hours"


# ============================================================
# 3. API Endpoints - ORM Read/Write Operations
# ============================================================

api = BoltAPI()


@api.get("/authors")
async def list_authors():
    """GET /authors - List all authors with book counts."""
    # ORM READ: Get all authors
    authors = Author.objects.all()

    # Serialize queryset (hot path optimization)
    serialized = AuthorSerializer.from_queryset(authors)

    return {
        "count": len(serialized),
        "authors": serialized
    }


@api.get("/authors/{author_id}")
async def get_author(author_id: int):
    """GET /authors/{id} - Get single author."""
    # ORM READ: Get single author
    author = await Author.objects.aget(id=author_id)

    # Serialize single instance
    return AuthorSerializer.from_model(author)


@api.post("/authors")
async def create_author(data: AuthorSerializer):
    """POST /authors - Create new author with validation."""
    # Data is already validated by AuthorSerializer!
    # Custom validators (validate_email, validate_name) were called

    # ORM WRITE: Create author
    author = await Author.objects.acreate(
        name=data.name,
        email=data.email,
        bio=data.bio
    )

    # Return created author
    return AuthorSerializer.from_model(author)


@api.put("/authors/{author_id}")
async def update_author(author_id: int, data: AuthorSerializer):
    """PUT /authors/{id} - Update author."""
    # ORM READ: Get existing author
    author = await Author.objects.aget(id=author_id)

    # ORM WRITE: Update fields
    author.name = data.name
    author.email = data.email
    author.bio = data.bio
    await author.asave()

    return AuthorSerializer.from_model(author)


@api.delete("/authors/{author_id}")
async def delete_author(author_id: int):
    """DELETE /authors/{id} - Delete author."""
    # ORM READ + WRITE: Delete author
    author = await Author.objects.aget(id=author_id)
    await author.adelete()

    return {"message": "Author deleted successfully"}


# ============================================================
# Book endpoints with nested author serialization
# ============================================================

@api.get("/books")
async def list_books():
    """GET /books - List all books with nested author info."""
    # ORM READ: Get all books with author (select_related for performance)
    books = Book.objects.select_related('author').all()

    # Serialize with nested authors
    serialized = [BookSerializer.from_model(book) async for book in books]

    return {
        "count": len(serialized),
        "books": serialized
    }


@api.get("/books/{book_id}")
async def get_book(book_id: int):
    """GET /books/{id} - Get single book with computed fields."""
    # ORM READ: Get book with author
    book = await Book.objects.select_related('author').aget(id=book_id)

    # Serialize (includes computed fields: price_category, reading_time)
    return BookSerializer.from_model(book)


@api.post("/books")
async def create_book(data: BookSerializer):
    """POST /books - Create book with validation."""
    # Data is validated (price > 0, pages > 0, title not empty, etc.)

    # ORM WRITE: Create book
    book = await Book.objects.acreate(
        title=data.title,
        author_id=data.author_id,
        description=data.description,
        price=data.price,
        pages=data.pages,
        published_date=data.published_date,
        is_published=data.is_published
    )

    # Fetch with author for nested serialization
    book = await Book.objects.select_related('author').aget(id=book.id)

    return BookSerializer.from_model(book)


@api.put("/books/{book_id}")
async def update_book(book_id: int, data: BookSerializer):
    """PUT /books/{id} - Update book."""
    # ORM READ: Get existing book
    book = await Book.objects.aget(id=book_id)

    # ORM WRITE: Update fields (with validation)
    book.title = data.title
    book.description = data.description
    book.price = data.price
    book.pages = data.pages
    book.published_date = data.published_date
    book.is_published = data.is_published
    if hasattr(data, 'author_id'):
        book.author_id = data.author_id

    await book.asave()

    # Reload with author
    book = await Book.objects.select_related('author').aget(id=book.id)

    return BookSerializer.from_model(book)


@api.get("/books/by-author/{author_id}")
async def get_books_by_author(author_id: int):
    """GET /books/by-author/{id} - Get all books by an author."""
    # ORM READ: Filter books by author
    books = Book.objects.filter(author_id=author_id).select_related('author')

    # Serialize list
    serialized = [BookSerializer.from_model(book) async for book in books]

    return {
        "author_id": author_id,
        "count": len(serialized),
        "books": serialized
    }


@api.get("/books/expensive")
async def get_expensive_books(min_price: float = 50.0):
    """GET /books/expensive?min_price=50 - Get books above price threshold."""
    # ORM READ: Filter by price
    books = Book.objects.filter(price__gte=min_price).select_related('author')

    serialized = [BookSerializer.from_model(book) async for book in books]

    return {
        "min_price": min_price,
        "count": len(serialized),
        "books": serialized
    }


# ============================================================
# Example Usage in Tests
# ============================================================

"""
Example API calls:

# Create author
POST /authors
{
    "name": "John Doe",
    "email": "john@example.com",
    "bio": "Bestselling author"
}

Response:
{
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "bio": "Bestselling author",
    "book_count": 0,
    "created_at": "2024-01-01T00:00:00Z"
}

# Create book with validation
POST /books
{
    "title": "Django Performance",
    "author_id": 1,
    "description": "Learn Django optimization",
    "price": 29.99,
    "pages": 350,
    "published_date": "2024-01-01",
    "is_published": true
}

Response:
{
    "id": 1,
    "title": "Django Performance",
    "description": "Learn Django optimization",
    "price": 29.99,
    "pages": 350,
    "published_date": "2024-01-01",
    "is_published": true,
    "author_id": 1,
    "author": {
        "id": 1,
        "name": "John Doe",
        "email": "john@example.com"
    },
    "price_category": "standard",
    "reading_time": "2.9 hours",
    "created_at": "2024-01-01T00:00:00Z"
}

# Validation error example
POST /books
{
    "title": "Bad Book",
    "author_id": 1,
    "price": -10,  # Invalid!
    "pages": 100
}

Response: 400 Bad Request
{
    "error": "Price must be positive"
}
"""
