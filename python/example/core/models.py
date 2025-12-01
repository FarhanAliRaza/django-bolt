from django.db import models

# Create your models here.


class Blog(models.Model):



    name = models.CharField(max_length=255)

    description = models.TextField()

    statuses = (
        ("published", "published"),
        ("draft", "draft"),
    )

    status = models.CharField(choices=statuses, max_length=100, default="draft")


