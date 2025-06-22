from django.db import models


class Referee(models.Model):
    name = models.CharField(max_length=128)
    refereeNumber = models.CharField(max_length=32, default=-1)

    def __str__(self):
        return f"{self.name} ({self.refereeNumber})"


class LichessAPIError(Exception):
    pass
