from django.db import models


class Author(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Blog(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    author = models.ForeignKey(Author, on_delete=models.CASCADE, null=True, blank=True, related_name="blogs")

    statuses = (
        ("published", "published"),
        ("draft", "draft"),
    )

    status = models.CharField(choices=statuses, max_length=100, default="draft")


