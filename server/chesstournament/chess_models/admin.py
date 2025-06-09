from django.contrib import admin

from chess_models.models.game import Game
from chess_models.models.other_models import Referee
from chess_models.models.player import Player
from chess_models.models.round import Round
from chess_models.models.tournament import Tournament

# Register your models here.

admin.site.register(Game)
admin.site.register(Player)
admin.site.register(Tournament)
admin.site.register(Round)
admin.site.register(Referee)