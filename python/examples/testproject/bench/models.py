from django.db import models


class BenchItem(models.Model):
    """Simple model for benchmarking CRUD operations without unique constraints."""
    name = models.CharField(max_length=100)
    value = models.IntegerField(default=0)
    description = models.TextField(blank=True, default="")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "bench_items"
        ordering = ["-created_at"]

    def __str__(self):
        return f"BenchItem({self.id}): {self.name}"
