from django.db import models
from django.contrib.auth.models import User
from chess_models.models.player import Player
from chess_models.models.other_models import Referee
from chess_models.models.constants import Scores, \
    TournamentType, TournamentSpeed, TournamentBoardType
from chess_models.models.constants import RankingSystem
from chess_models.models.round import Round
from chess_models.models.game import Game
from rest_framework import serializers


class RankingSystemClass(models.Model):
    value = models.CharField(
        max_length=2,
        choices=RankingSystem.choices,
        primary_key=True
    )


RANK = 'rank'


class Tournament(models.Model):
    name = models.CharField(max_length=128, unique=True,
                            blank=True, null=True)
    administrativeUser = models.ForeignKey(User, on_delete=models.DO_NOTHING,
                                           null=True, blank=True)
    players = models.ManyToManyField(Player, through='TournamentPlayers',
                                     blank=True)
    referee = models.ForeignKey(Referee, on_delete=models.DO_NOTHING,
                                null=True, blank=True)
    start_date = models.DateField(auto_now_add=True, null=True)
    end_date = models.DateField(null=True, blank=True)
    max_update_time = models.IntegerField(default=43200)
    only_administrative = models.BooleanField(default=False)
    tournament_type = models.CharField(max_length=2,
                                       choices=TournamentType.choices,
                                       null=True)
    tournament_speed = models.CharField(max_length=2,
                                        choices=TournamentSpeed.choices,
                                        null=True)
    board_type = models.CharField(max_length=3,
                                  choices=TournamentBoardType.choices,
                                  null=True)
    win_points = models.FloatField(default=1.0)
    draw_points = models.FloatField(default=0.5)
    lose_points = models.FloatField(default=0.0)
    timeControl = models.CharField(max_length=32, default='15+0')
    number_of_rounds_for_swiss = models.IntegerField(default=0)
    rankingList = models.ManyToManyField(RankingSystemClass, blank=True)

    def getScores(self):
        scores = {player: self._getPlayerDict(player)
                  for player in self.getPlayers()}
        self.getBlackWins(scores)
        return {player: scores[player] for player in scores}

    def _getPlayerDict(self, player):
        games = self._getPlayerGames(player)
        wins, draws, loses, blacks = self._getPlayerStats(games, player)
        byes = self._getPlayerSpecialStats(games, player)

        plain_points = wins * self.win_points + draws * self.draw_points\
            + loses * self.lose_points + byes

        return {RankingSystem.PLAIN_SCORE.value: plain_points,
                RankingSystem.WINS.value: wins,
                RankingSystem.BLACKTIMES.value: blacks,
                RANK: 0
                }

    def _compareScores(self, p1, p2, scores):
        for key in scores[p1].keys():
            if scores[p1][key] > scores[p2][key]:
                return 1
            elif scores[p1][key] < scores[p2][key]:
                return -1
        return 0

    def _getPlayerGames(self, player):
        games = []
        for round in Round.objects.filter(tournament=self):
            for game in Game.objects.filter(round=round):
                if game.white == player or game.black == player:
                    games.append(game)
        return games

    def _getPlayerStats(self, games, player):
        wins, draws, loses, blacks = 0, 0, 0, 0
        for game in games:
            result = game.result

            if game.black == player:
                blacks += 1

            # DRAW
            if result == Scores.DRAW:
                draws += 1
            # WIN
            elif (
                (game.white == player and result == Scores.WHITE) or
                (game.black == player and result == Scores.BLACK)
            ):
                wins += 1
            # LOSE
            elif (
                (game.white == player and result == Scores.BLACK) or
                (game.black == player and result == Scores.WHITE)
            ):
                loses += 1
            # BYES IGNORED
            elif result in [Scores.FORFEITWIN, Scores.BYE_H,
                            Scores.BYE_F, Scores.BYE_U, Scores.BYE_Z]:
                continue
        return wins, draws, loses, blacks

    def _getPlayerSpecialStats(self, games, player):
        byes_f = 0
        byes_h = 0
        fortwin = 0
        for game in games:
            if game.result in [Scores.BYE_F, Scores.BYE_U]:
                byes_f += 1
            elif game.result == Scores.BYE_H:
                byes_h += 1
            elif (game.result == Scores.FORFEITWIN and game.white == player):
                fortwin += 1
            byes = byes_f * self.win_points + byes_h * self.draw_points\
                + fortwin * self.win_points
        return byes

    def getBlackWins(self, scores):
        for player in scores.keys():
            scores[player][RankingSystem.BLACKTIMES]\
                = self._getBlackTimes(player)
            scores[player][RankingSystem.WINS]\
                = self._getPlayerWins(player)
        return scores

    def _getBlackTimes(self, player):
        blackTimes = 0
        for game in self._getPlayerGames(player):
            if game.black == player and game.result != Scores.FORFEITWIN:
                blackTimes += 1
        return blackTimes

    def _getBlackWins(self, player):
        blackWins = 0
        for game in self._getPlayerGames(player):
            if game.black == player and (game.result == Scores.BLACK):
                blackWins += 1
        return blackWins

    def _getPlayerWins(self, player):
        wins = 0
        for game in self._getPlayerGames(player):
            if (game.white == player and game.result == Scores.WHITE
                    or game.black == player and game.result == Scores.BLACK):
                wins += 1
        return wins

    def getRanking(self):

        buchholz_in_ranking = any(rs.value == 'BU'
                                  for rs in self.getRankingList())
        buchholzcut1_in_ranking = any(rs.value == 'BC'
                                      for rs in self.getRankingList())
        pseudobuchholz_in_ranking = any(rs.value == 'PB'
                                        for rs in self.getRankingList())

        if (pseudobuchholz_in_ranking):
            scores = {}
            scores = self.getPseudoBuchholz()
            ranked_players = sorted(
                scores.keys(),
                key=lambda p: (scores[p][RankingSystem.PSEUDOBUCH],
                               scores[p][RankingSystem.PLAIN_SCORE]),
                reverse=True
            )
        elif (buchholzcut1_in_ranking):
            scores = {}
            scores = self.getBuchholzCutMinusOne(
                self.getAdjustedScores
                (self.getOpponents(scores)))
            ranked_players = sorted(
                scores.keys(),
                key=lambda p: (scores[p][RankingSystem.BUCHHOLZ_CUT1],
                               scores[p][RankingSystem.PLAIN_SCORE]),
                reverse=True
            )
        elif (buchholz_in_ranking):
            scores = {}
            scores = self.getBuchholz(
                self.getAdjustedScores
                (self.getOpponents(scores)))
            ranked_players = sorted(
                scores.keys(),
                key=lambda p: (scores[p][RankingSystem.BUCHHOLZ],
                               scores[p][RankingSystem.PLAIN_SCORE]),
                reverse=True
            )
        else:
            scores = self.getScores()
            ranked_players = sorted(
                scores.keys(),
                key=lambda p: (
                    scores[p].get(RankingSystem.PLAIN_SCORE, 0),
                    scores[p].get(RankingSystem.WINS.value, 0),
                    scores[p].get(RankingSystem.BLACKTIMES.value, 0)
                ),
                reverse=True
            )

        for i, player in enumerate(ranked_players):
            scores[player][RANK] = i + 1

        return scores

    def getPlayers(self, sorted: bool = False):
        if not sorted:
            tournament_players = self.players.filter(tournament=self)\
                .order_by('creation_date')
            return {
                player: {
                    'rank': i + 1
                }
                for i, player in enumerate(tournament_players)
            }

        queryset = self.players.all()
        if self.board_type == TournamentBoardType.LICHESS:
            if self.tournament_speed == TournamentSpeed.RAPID:
                ordered_players = queryset\
                    .order_by('lichess_rating_rapid').reverse()
            elif self.tournament_speed == TournamentSpeed.BLITZ:
                ordered_players = queryset\
                    .order_by('lichess_rating_blitz').reverse()
            elif self.tournament_speed == TournamentSpeed.CLASSICAL:
                ordered_players = queryset\
                    .order_by('lichess_rating_classical').reverse()
            elif self.tournament_speed == TournamentSpeed.BULLET:
                ordered_players = queryset\
                    .order_by('lichess_rating_bullet').reverse()
            else:
                ordered_players = queryset

        elif self.board_type == TournamentBoardType.OTB:
            if self.tournament_speed == TournamentSpeed.CLASSICAL:
                ordered_players = queryset\
                    .order_by('fide_rating_classical').reverse()
            else:
                ordered_players = queryset
        else:
            ordered_players = queryset
        return list(ordered_players)

    def getPlayersCount(self):
        return len(TournamentPlayers.objects.filter(tournament=self))

    def getOpponents(self, scores):
        players = self.getPlayers()
        results = {}

        for player in players:
            opponents = []
            OTBopponents = []
            result = []
            voluntarellyUmplayed = []
            white_count = 0
            black_count = 0

            games = self._getPlayerGames(player)

            for game in games:
                is_white = game.white == player
                is_black = game.black == player

                if is_white:
                    opponent = game.black
                    if (game.black is not None
                            and game.result != Scores.FORFEITWIN):
                        white_count += 1
                elif is_black:
                    opponent = game.white
                    if (game.result != Scores.FORFEITWIN):
                        black_count += 1
                else:
                    continue

                if game.result == Scores.WHITE:
                    pt = 1.0 if is_white else 0.0
                elif game.result == Scores.BLACK:
                    pt = 1.0 if is_black else 0.0
                elif game.result == Scores.DRAW:
                    pt = 0.5
                elif game.result == Scores.FORFEITWIN:
                    pt = 1.0 if (is_white) else 0.0
                    if opponent is not None:
                        if (is_black):
                            voluntarellyUmplayed.append(player)
                        opponent = player
                elif game.result in [Scores.BYE_F, Scores.BYE_U]:
                    pt = 1.0
                elif game.result == Scores.BYE_H:
                    pt = 0.5
                    if opponent is None:
                        voluntarellyUmplayed.append(player)
                elif game.result == Scores.FORFEITLOSS\
                        or game.result == Scores.BYE_Z:
                    pt = 0.0
                    if opponent is None:
                        voluntarellyUmplayed.append(player)
                else:
                    pt = 0.0

                result.append(pt)
                if opponent:
                    opponents.append(opponent)
                    if game.result in [Scores.WHITE,
                                       Scores.BLACK, Scores.DRAW]:
                        OTBopponents.append(opponent)
                else:
                    opponents.append(player)
            results[player] = {
                'opponents': opponents,
                'OTBopponents': OTBopponents,
                'result': result,
                'voluntarellyUmplayed': voluntarellyUmplayed,
                'colordifference': white_count - black_count
            }

        return results

    def getBuchholz(tournament, adjustedScores):
        scores = tournament.getScores()
        playersList = tournament.getOpponents(scores)

        buchholz_scores = {}

        for player, data in playersList.items():
            opponents = data['opponents']
            total = 0

            for opponent in opponents:
                if opponent and opponent != player:
                    opponent_score = adjustedScores[opponent]['adjustedScore']
                elif opponent == player:
                    opponent_score = scores[opponent]['PS']

                total += opponent_score

            buchholz_scores[player] = {
                'PS': scores.get(player, {}).get('PS', 0.0),
                RankingSystem.PLAIN_SCORE: scores.get(player, {})
                .get(RankingSystem.PLAIN_SCORE, 0.0),
                'adjustedScore': adjustedScores[player]['adjustedScore'],
                RankingSystem.BUCHHOLZ: total,
            }

        return buchholz_scores

    def getAdjustedScores(tournament, playersList):

        adjustedScores = {}

        for player, data in playersList.items():
            results = data['result']
            base_score = sum(results)
            bonus = 0.0

            if (len(data['OTBopponents']) < 2):
                bonus = 1.0

            adjusted = base_score + bonus

            adjustedScores[player] = {
                RankingSystem.PLAIN_SCORE: base_score,
                'adjustedScore': adjusted
            }

        return adjustedScores

    def getBuchholzCutMinusOne(self, getAdjustedScoresList):
        scores = self.getScores()
        playersList = self.getOpponents(scores)
        buchholz_scores = self.getBuchholz(getAdjustedScoresList)

        buchholzc1_scores = {}

        for player, data in playersList.items():
            opponents = data['opponents']
            opponent_scores = []
            volunplayed = 0

            for opponent in opponents:
                if opponent and opponent != player:
                    score = getAdjustedScoresList[opponent]['adjustedScore']
                    opponent_scores.append(score)
                elif opponent == player:
                    if (len(playersList[player]['voluntarellyUmplayed']) == 0):
                        opponent_scores.append(scores[opponent]['PS'])
                    else:
                        volunplayed += 1
                        if (volunplayed > 1):
                            opponent_scores.append(scores[opponent]['PS'])
                        else:
                            opponent_scores.append(0.0)

            non_zero_scores = [s for s in opponent_scores if s != 0.0]

            if len(non_zero_scores) > 4:
                opponent_scores.remove(min(non_zero_scores))

            total = sum(opponent_scores)

            buchholzc1_scores[player] = {
                'PS': scores.get(player, {}).get('PS', 0.0),
                RankingSystem.WINS.value: self._getPlayerWins(player),
                RankingSystem.BLACKTIMES.value: self._getBlackTimes(player),
                RankingSystem.PLAIN_SCORE: scores.get(player, {})
                .get(RankingSystem.PLAIN_SCORE, 0.0),
                'adjustedScore':
                    getAdjustedScoresList[player]['adjustedScore'],
                RankingSystem.BUCHHOLZ:
                    buchholz_scores[player][RankingSystem.BUCHHOLZ],
                RankingSystem.BUCHHOLZ_CUT1: total,
            }

        return buchholzc1_scores

    def getMediamBuchholz(self):
        pass

    def getSonnebornBerger(self):
        pass

    def getPseudoBuchholz(self):
        scores = self.getScores()
        playersList = self.getOpponents(scores)

        pseudobuchholz_scores = {}

        for player, data in playersList.items():
            opponents = data['opponents']
            total = 0

            for opponent in opponents:
                total += scores[opponent][RankingSystem.PLAIN_SCORE]

            total = total / len(opponents)

            pseudobuchholz_scores[player] = {
                RankingSystem.WINS.value: self._getPlayerWins(player),
                RankingSystem.BLACKTIMES.value: self._getBlackTimes(player),
                RankingSystem.PLAIN_SCORE: scores.get(
                    RankingSystem.PLAIN_SCORE, 0.0),
                RankingSystem.PSEUDOBUCH: total
            }
        return pseudobuchholz_scores

    def getRankingList(self):
        return RankingSystemClass.objects.filter(tournament=self)

    def cleanRankingList(self):
        RankingSystemClass.objects.filter(tournament=self).delete()

    def getRoundCount(self):
        return len(Round.objects.filter(tournament=self.id))

    def get_number_of_rounds_with_games(self):
        count = 0
        for round in Round.objects.filter(tournament=self):
            if len(Game.objects.filter(round=round).filter(finished=True)) > 0:
                count += 1
                continue
        return count

    def get_latest_round_with_games(self):
        rounds = Round.objects.filter(tournament=self)
        i = len(rounds)
        while i > 0:
            i -= 1
            if len(Game.objects.filter(round=rounds[i])
                   .filter(finished=True)) > 0:
                return rounds[i]
        return None

    def addToRankingList(self, rankingSystem: RankingSystem):
        ranking_system_obj, _ = RankingSystemClass.objects\
            .get_or_create(value=rankingSystem)
        self.rankingList.add(ranking_system_obj)

    def removeFromRankingList(self, rankingSystem: RankingSystem):
        ranking_system_obj, _ = RankingSystemClass.objects\
            .get_or_create(value=rankingSystem)
        self.rankingList.remove(ranking_system_obj)

    def getGamesCount(self, finished):
        return Game.objects.filter(round__tournament=self, finished=finished)\
            .count()

    def getGames(self):
        return Game.objects.filter(round__tournament=self)

    def __str__(self):
        return f"tournament_{self.id:02}"


class TournamentPlayers(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.DO_NOTHING)
    player = models.ForeignKey(Player, on_delete=models.DO_NOTHING)
    date = models.DateTimeField(auto_created=True, auto_now_add=True)

    class Meta:
        unique_together = ('tournament', 'player')
        ordering = ['date',]


class RankingSystemClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = RankingSystemClass
        fields = ['value']


class TournamentSerializer(serializers.ModelSerializer):
    players = serializers.CharField(write_only=True)

    class Meta:
        model = Tournament
        fields = [
            'id',
            'name',
            'administrativeUser',
            'players',
            'referee',
            'start_date',
            'end_date',
            'max_update_time',
            'only_administrative',
            'tournament_type',
            'tournament_speed',
            'board_type',
            'win_points',
            'draw_points',
            'lose_points',
            'timeControl',
            'number_of_rounds_for_swiss',
            'rankingList'
        ]

    def create(self, validated_data):
        players_raw = validated_data.pop('players')
        tournament = Tournament.objects.create(**validated_data)

        usernames = [line.strip() for line in players_raw.strip()
                     .split('\n') if line.strip()
                     and line.strip() != 'lichess_username']

        for username in usernames:
            player = Player.objects.get(lichess_username=username)
            tournament.players.add(player)

        return tournament
