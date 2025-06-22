from django.db import models
from django.utils import timezone


class Round(models.Model):
    name = models.CharField(max_length=128)
    tournament = models.ForeignKey('Tournament', on_delete=models.DO_NOTHING)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateField(null=True, blank=True)
    finish = models.BooleanField(default=False)

    def __str__(self):
        return self.name
