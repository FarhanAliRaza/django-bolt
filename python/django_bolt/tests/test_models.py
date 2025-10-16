"""
Test models for Django ORM integration tests.

These models are used to verify that ViewSets work with real Django ORM operations.
"""
from django.db import models


class Article(models.Model):
    """Test model for ViewSet/Mixin Django ORM integration tests."""

    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.CharField(max_length=100)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'django_bolt'
        ordering = ['-created_at']

    def __str__(self):
        return self.title
