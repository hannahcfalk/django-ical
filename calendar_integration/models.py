from django.db import models
from django.utils import timezone


class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    start_datetime = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title
