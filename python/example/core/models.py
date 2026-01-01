from django.db import models


class Blog(models.Model):
    name = models.CharField(max_length=255)

    description = models.TextField()

    statuses = (
        ("published", "published"),
        ("draft", "draft"),
    )

    status = models.CharField(choices=statuses, max_length=100, default="draft")


class Document(models.Model):
    """Document model for file upload examples."""

    title = models.CharField(max_length=255)
    file = models.FileField(upload_to="documents/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
