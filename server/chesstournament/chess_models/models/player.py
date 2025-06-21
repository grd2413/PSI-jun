from django.forms import ValidationError
import requests
from django.db import models
from.other_models import LichessAPIError
from rest_framework import serializers


class Player(models.Model):
    name = models.CharField(max_length=256, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    country = models.CharField(max_length=2, null=True, blank=True)
    lichess_username = models.CharField(max_length=255, unique=True, null=True, blank=True)
    lichess_rating_bullet = models.IntegerField(default=0)
    lichess_rating_blitz = models.IntegerField(default=0)
    lichess_rating_rapid = models.IntegerField(default=0)
    lichess_rating_classical = models.IntegerField(default=0)
    
    fide_id = models.IntegerField(unique=True, null=True, default=None)
    fide_rating_blitz = models.IntegerField(default=0)
    fide_rating_rapid = models.IntegerField(default=0)
    fide_rating_classical = models.IntegerField(default=0)
    
    creation_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('name', 'email')
        ordering = ['-creation_date']

    def fetch_lichess_data(self):
        if self.lichess_username:
            url = f"https://lichess.org/api/user/{self.lichess_username}"
            response = requests.get(url,timeout=5000)
            if response.status_code == 200:
                data = response.json()
                perfs = data.get("perfs", {})
                self.lichess_rating_bullet = perfs.get("bullet", {}).get("rating", 0)
                self.lichess_rating_blitz = perfs.get("blitz", {}).get("rating", 0)
                self.lichess_rating_rapid = perfs.get("rapid", {}).get("rating", 0)
                self.lichess_rating_classical = perfs.get("classical", {}).get("rating", 0)
            elif response.status_code == 404:
                raise ValidationError(f"El usuario {self.lichess_username} no existe en Lichess.")
            else:
                raise ValidationError(f"Error al obtener datos de Lichess para {self.lichess_username}: {response.status_code}")

    def check_lichess_user_exists(self):
        if self.lichess_username and self.lichess_username is not None:
            url = f"https://lichess.org/api/user/{self.lichess_username}"
            response = requests.get(url)
            return response.status_code == 200
        return False

    def get_lichess_user_ratings(self):
        if self.lichess_username:
            url = f"https://lichess.org/api/user/{self.lichess_username}"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                perfs = data.get("perfs", {})
                self.lichess_rating_bullet = perfs.get("bullet", {}).get("rating", 0)
                self.lichess_rating_blitz = perfs.get("blitz", {}).get("rating", 0)
                self.lichess_rating_rapid = perfs.get("rapid", {}).get("rating", 0)
                self.lichess_rating_classical = perfs.get("classical", {}).get("rating", 0)
            elif response.status_code == 404:
                raise LichessAPIError(f"El usuario {self.lichess_username} no existe en Lichess.")
            else:
                raise LichessAPIError(f"Error al obtener datos de Lichess para {self.lichess_username}: {response.status_code}")
    
    def save(self, *args, **kwargs):
        existing_player = Player.objects.filter(
            models.Q(name=self.name, name__isnull=False, email=self.email, email__isnull=False) |
            models.Q(lichess_username=self.lichess_username, lichess_username__isnull=False) |
            models.Q(fide_id=self.fide_id, fide_id__isnull=False)
        ).exclude(id=self.id).first()
        self.fetch_lichess_data()
        if existing_player:
            for field in self._meta.fields:
                if getattr(self, field.name) is not None:
                    setattr(existing_player, field.name, getattr(self, field.name))
            self.id = existing_player.id
            self.creation_date = existing_player.creation_date
            kwargs.pop('force_insert', None)
            return super(Player, self).save(*args, **kwargs)
        
        return super().save(*args, **kwargs)
    
    def __str__(self):
        if self.lichess_username:
            return self.lichess_username
        return self.name


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ['lichess_username']