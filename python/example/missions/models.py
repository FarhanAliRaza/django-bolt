from __future__ import annotations

from django.db import models


class Mission(models.Model):
    STATUS_CHOICES = [
        ("planned", "Planned"),
        ("active", "Active"),
        ("completed", "Completed"),
        ("aborted", "Aborted"),
    ]

    name = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="planned")
    launch_date = models.DateTimeField(null=True, blank=True)
    description = models.TextField(blank=True)
    patch_image = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name


class Astronaut(models.Model):
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=50)
    mission = models.ForeignKey(
        Mission, on_delete=models.CASCADE, related_name="astronauts"
    )

    def __str__(self):
        return f"{self.name} ({self.role})"
