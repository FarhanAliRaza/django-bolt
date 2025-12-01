from django.db import models


class User(models.Model):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField()
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username

    class Meta:
        ordering = ['username']

