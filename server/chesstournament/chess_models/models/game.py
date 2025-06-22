from django.db import models
from chess_models.models.player import Player
from chess_models.models.round import Round
from chess_models.models.constants import Scores, TournamentType
from rest_framework import serializers
import requests

from .other_models import LichessAPIError


class Game(models.Model):
    white = models.ForeignKey(Player, related_name='white_games',
                              on_delete=models.DO_NOTHING, null=True,
                              blank=True)
    black = models.ForeignKey(Player, related_name='black_games',
                              on_delete=models.DO_NOTHING, null=True,
                              blank=True)
    finished = models.BooleanField(default=False)
    round = models.ForeignKey(Round, on_delete=models.DO_NOTHING)
    start_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    result = models.CharField(max_length=1, default=Scores.NOAVAILABLE)
    rankingOrder = models.IntegerField(default=0)

    def get_lichess_game_result(self, game_id=None):

        if game_id is None:
            game_id = self.id
        url = f" https://lichess.org/api/game/{game_id}"

        try:
            response = requests.get(url)
            response.raise_for_status()

            data = response.json()

            white_player_lichess = data['players']['white']['userId'].lower()
            black_player_lichess = data['players']['black']['userId'].lower()

            white_player = self.white.lichess_username.lower()
            black_player = self.black.lichess_username.lower()

            if (white_player != white_player_lichess
                    or black_player != black_player_lichess):
                raise LichessAPIError(f"Players for game {game_id} \
                                      are different")

            winner = data.get('winner')
            self.finished = True
            if winner == 'white':
                result = Scores.WHITE
            elif winner == 'black':
                result = Scores.BLACK
            elif winner is None:
                result = Scores.DRAW
            else:
                result = Scores.NOAVAILABLE

            self.result = result
            self.save(using='default')

            return result, white_player, black_player

        except requests.exceptions.RequestException as e:
            raise LichessAPIError(
                f"Failed to fetch data for game {game_id}: {str(e)}"
            )
        except LichessAPIError as e:
            raise LichessAPIError(f"Error con el juego ID {game_id}: {str(e)}")

    def __str__(self):
        white = f"{self.white}({self.white.id})" if self.white else "(BYE)"
        black = f"{self.black}({self.black.id})" if self.black else "(BYE)"
        result = Scores(self.result).label if self.result else "—"
        return f"{white} vs {black} = {result}"


def create_rounds(tournament, swissByes=[]):
    players = tournament.getPlayers(sorted=True)
    num_players = tournament.getPlayersCount()
    rounds = []

    if (tournament.tournament_type == TournamentType.ROUNDROBIN):
        rounds_schedule = berger_rounds(num_players)
        for round_number in range(num_players - 1):
            round_instance = Round.objects.create(tournament=tournament,
                                                  name=f"Rd {round_number+1}")
            current_round = []
            for round_game in range(num_players // 2):
                white_idx = rounds_schedule[round_number][round_game][0]
                black_idx = rounds_schedule[round_number][round_game][1]
                current_round.append(Game.objects.create(
                    white=players[white_idx],
                    black=players[black_idx],
                    round=round_instance,
                    result=Scores.NOAVAILABLE,
                    finished=False
                ))
            rounds.append(current_round)
    elif (tournament.tournament_type ==
          TournamentType.DOUBLEROUNDROBINSAMEDAY):
        rounds_schedule = rb_rounds(num_players)
    elif (tournament.tournament_type == TournamentType.SWISS):
        return create_swiss_first_round(tournament, swissByes)

    return rounds


def rb_rounds(num_players):
    half = num_players // 2
    players = list(range(num_players))
    pivot = players[-1]
    barrel = list(reversed(players[:-1]))
    rounds = []

    for round_nr in range(num_players - 1):
        even_round = round_nr % 2 == 0
        pairs = []

        pair = (pivot, barrel[-1])
        if even_round:
            pair = (barrel[-1], pivot)
        pairs.append(pair)

        for idx in range(half - 1):
            p1 = barrel[idx]
            p2 = barrel[-(idx + 2)]
            pair = (p2, p1) if even_round else (p1, p2)
            pairs.append(pair)

        rounds.append(pairs)
        rounds.append([(b, w) for (w, b) in pairs])

        barrel = barrel[half - 1:] + barrel[:half - 1]

    return rounds


def berger_rounds(num_players):
    assert num_players > 0
    half = num_players // 2
    players = [i for i in range(num_players)]
    pivot = players[-1]
    barrel = list(reversed(players[:-1]))
    rounds = []
    for round_nr in range(num_players-1):
        even_round = round_nr % 2 == 0
        pairs = []
        pair = (pivot, barrel[-1])
        if even_round:
            pair = list(reversed(pair))
        pairs.append(pair)
        even_round = True
        for idx in range(half-1):
            pair = (barrel[idx], barrel[-(idx+1+1)])
            if even_round:
                pair = list(reversed(pair))
            pairs.append(pair)
        rounds.append(pairs)
        barrel = barrel[half-1:] + barrel[:half-1]
    return rounds


def create_swiss_first_round(tournament, swissByes=None):
    if swissByes is None:
        swissByes = []

    players = list(tournament.getPlayers(sorted=True))
    players.sort(key=lambda p: p.fide_rating_classical or 0, reverse=True)
    players_by_id = {p.id: p for p in players}
    num_players = len(players)

    bye_players = []

    for pid in swissByes:
        player = players_by_id[pid]
        bye_players.append((player, Scores.BYE_H))

    all_bye_ids = set(p[0].id for p in bye_players)
    if (num_players - len(all_bye_ids)) % 2 == 1:
        candidates = [p for p in reversed(players) if p.id not in all_bye_ids]
        if candidates:
            bye_unplayed = candidates[0]
            bye_players.append((bye_unplayed, Scores.BYE_U))
            all_bye_ids.add(bye_unplayed.id)

    players_to_pair = [p for p in players if p.id not in all_bye_ids]

    round_instance = Round.objects.create(tournament=tournament, name="Rd 1")
    games = []

    for player, result in bye_players:
        games.append(Game.objects.create(
            white=player,
            black=None,
            round=round_instance,
            result=result,
            finished=False
        ))

    players_to_pair.sort(key=lambda p:
                         p.fide_rating_classical or 0,
                         reverse=True)
    half = len(players_to_pair) // 2
    for i in range(half):
        white = players_to_pair[i]
        black = players_to_pair[i + half]
        games.append(Game.objects.create(
            white=white,
            black=black,
            round=round_instance,
            result=Scores.NOAVAILABLE,
            finished=False
        ))

    return games


class GameSerializer(serializers.ModelSerializer):
    white = serializers.StringRelatedField()
    black = serializers.StringRelatedField()
    round = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Game
        fields = [
            'id',
            'white',
            'black',
            'finished',
            'round',
            'start_date',
            'update_date',
            'result',
            'rankingOrder'
        ]
