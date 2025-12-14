"""
Test models for Django ORM integration tests.

These models are used to verify that ViewSets work with real Django ORM operations.
"""
from django.db import models


class Article(models.Model):
    """Test model for ViewSet/Mixin Django ORM integration tests."""

    statuses = (
        (
            "draft",
            "draft"
        ),
        (
            "published",
            "published"

        )
    )

    title = models.CharField(max_length=200)
    content = models.TextField()
    status = models.CharField(
        choices=statuses, default="draft", max_length=100
    )
    author = models.CharField(max_length=100)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'django_bolt'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Author(models.Model):
    """Author model for testing nested ForeignKey relationships."""

    name = models.CharField(max_length=200)
    email = models.EmailField()
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'django_bolt'

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Tag model for testing nested many-to-many relationships."""

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        app_label = 'django_bolt'

    def __str__(self):
        return self.name


class BlogPost(models.Model):
    """BlogPost model with ForeignKey to Author and M2M to Tags."""

    title = models.CharField(max_length=300)
    content = models.TextField()
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='posts')
    tags = models.ManyToManyField(Tag, related_name='posts')
    published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'django_bolt'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Comment(models.Model):
    """Comment model with ForeignKey to both Author and BlogPost."""

    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'django_bolt'
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.author.name} on {self.post.title}"


class User(models.Model):
    """Custom user model for testing authentication flows."""

    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password_hash = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'django_bolt'
        ordering = ['-created_at']

    def __str__(self):
        return self.username


class UserProfile(models.Model):
    """User profile with one-to-one relationship to User."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True)
    avatar_url = models.URLField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'django_bolt'

    def __str__(self):
        return f"Profile for {self.user.username}"


class Event(models.Model):
    """Event model for testing unique_together constraints."""

    name = models.CharField(max_length=200)
    venue = models.CharField(max_length=200)
    date = models.DateField()
    start_time = models.TimeField()

    class Meta:
        app_label = 'django_bolt'
        unique_together = [('venue', 'date', 'start_time')]

    def __str__(self):
        return f"{self.name} at {self.venue}"


class DailyReport(models.Model):
    """DailyReport model for testing unique_for_date constraints."""

    title = models.CharField(max_length=200, unique_for_date='report_date')
    report_date = models.DateField()
    content = models.TextField()

    class Meta:
        app_label = 'django_bolt'

    def __str__(self):
        return f"{self.title} - {self.report_date}"


class MonthlyReport(models.Model):
    """MonthlyReport model for testing unique_for_month constraints."""

    category = models.CharField(max_length=100, unique_for_month='report_date')
    report_date = models.DateField()
    summary = models.TextField()

    class Meta:
        app_label = 'django_bolt'

    def __str__(self):
        return f"{self.category} - {self.report_date.strftime('%Y-%m')}"


class YearlyReport(models.Model):
    """YearlyReport model for testing unique_for_year constraints."""

    department = models.CharField(max_length=100, unique_for_year='report_date')
    report_date = models.DateField()
    annual_summary = models.TextField()

    class Meta:
        app_label = 'django_bolt'

    def __str__(self):
        return f"{self.department} - {self.report_date.year}"


class AbstractBaseModel(models.Model):
    """Abstract base model for testing is_abstract_model()."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        app_label = 'django_bolt'


class ConcreteModel(AbstractBaseModel):
    """Concrete model that inherits from abstract base."""

    name = models.CharField(max_length=100)

    class Meta:
        app_label = 'django_bolt'

    def __str__(self):
        return self.name
