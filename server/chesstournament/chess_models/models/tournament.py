from datetime import timezone
from functools import cmp_to_key
from django.db import models
from django.contrib.auth.models import User
from chess_models.models.player import Player
from chess_models.models.other_models import Referee
from chess_models.models.constants import Scores, TournamentType, TournamentSpeed, TournamentBoardType
from chess_models.models.constants import RankingSystem
from chess_models.models.round import Round
from chess_models.models.game import Game
from rest_framework import serializers

class  RankingSystemClass(models.Model):
    value = models.CharField(
        max_length=2,
        choices=RankingSystem.choices,
        primary_key=True
    )

RANK = 'rank'

class Tournament(models.Model):
    name = models.CharField(max_length=128, unique=True, blank=True, null=True)
    administrativeUser = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, blank=True)
    players = models.ManyToManyField(Player, through='TournamentPlayers', blank=True)
    referee = models.ForeignKey(Referee, on_delete=models.DO_NOTHING, null=True, blank=True)
    start_date = models.DateField(auto_now_add=True, null=True)
    end_date = models.DateField(null=True, blank=True)
    max_update_time = models.IntegerField(default=43200)
    only_administrative = models.BooleanField(default=False)
    tournament_type = models.CharField(max_length=2, choices=TournamentType.choices, null=True)
    tournament_speed = models.CharField(max_length=2, choices=TournamentSpeed.choices, null=True)
    board_type = models.CharField(max_length=3, choices=TournamentBoardType.choices, null=True)
    win_points = models.FloatField(default=1.0)
    draw_points = models.FloatField(default=0.5)
    lose_points = models.FloatField(default=0.0)
    timeControl = models.CharField(max_length=32, default='15+0')
    number_of_rounds_for_swiss = models.IntegerField(default=0)
    rankingList = models.ManyToManyField(RankingSystemClass, blank=True)

    def getScores(self):
            scores = {player: self._getPlayerDict(player) for player in self.getPlayers()}
            sorted_players = [x for x in scores.keys()]
            #sorted_players.sort(key=cmp_to_key(lambda p1, p2 : self._compareScores(p1, p2, scores)), reverse=True)
            return {player: scores[player] for player in sorted_players}

    def _getPlayerDict(self, player):
        games = self._getPlayerGames(player)
        wins, draws, loses, blacks = self._getPlayerStats(games, player)
        byes = self._getPlayerSpecialStats(games, player)
        #plain_points = (wins + byes) * self.win_points + draws * self.draw_points + loses * self.lose_points
        plain_points = wins * self.win_points + draws * self.draw_points + loses * self.lose_points + byes
        
        #print("Player: "+ player.name + " b: " + str(byes) + " w: " + str(wins) + " t: " + str(draws) + " l: " + str(loses) + " TOTAL: " + str(plain_points) + "\n")
        #return {RankingSystem.PLAIN_SCORE.value: plain_points}
        return {RankingSystem.PLAIN_SCORE.value: plain_points,
                RankingSystem.WINS.value: wins,
                RankingSystem.BLACKTIMES.value: blacks,
                RANK: 0
            }
    
    def _compareScores(self, p1, p2, scores):
        # for key in [x.value for x in self.getRankingList()]:
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
            if game.result == Scores.DRAW:
                draws+=1
            elif game.white == player:
                if game.result == Scores.WHITE:
                    wins+=1
                else:
                    loses+=1
            elif game.black == player:
                blacks+=1
                if game.result == Scores.BLACK:
                    wins+=1    
                else:
                    loses+=1
        return wins, draws, loses, blacks

    def _getPlayerSpecialStats(self, games, player):
        byes = 0
        for game in games:
            if game.result == Scores.BYE_F:
                byes+=1
            elif game.result == Scores.BYE_H:
                byes+=1
        return byes

    def getBlackWins(self, scores):
        for player in scores.keys():
            print(player, self._getBlackWins(player),  self._getPlayerWins(player))
            scores[player][RankingSystem.BLACKTIMES.value] = 0
            scores[player][RankingSystem.WINS.value] = 0
        return scores
    
    def _getBlackWins(self, player):
        blackWins = 0
        for game in self._getPlayerGames(player):
            if game.black == player and game.result == Scores.BLACK:
                blackWins += 1
        return blackWins

    def _getPlayerWins(self, player):
        wins = 0
        for game in self._getPlayerGames(player):
            if  game.white == player and game.result == Scores.WHITE or\
                game.black == player and game.result == Scores.BLACK:
                wins += 1
        return wins
    
    def getRanking(self):
        scores = self.getScores()
        ranked_players = [x for x in scores.keys()]
        ranked_players.sort(key=cmp_to_key(lambda p1, p2 : self._compareScores(p1, p2, scores)), reverse=True)
        for i in range(len(ranked_players)):
            scores[ranked_players[i]][RANK] = i + 1
        return scores

    def getPlayers(self, sorted:bool=False):
        if not sorted:
            tournament_players = self.players.filter(tournament=self).order_by('creation_date')
            return {
                player: {
                    'rank': i + 1
                }
                for i, player in enumerate(tournament_players)  
            }
        
        queryset = self.players.all()
        rank = ""
        if self.board_type == TournamentBoardType.LICHESS:
            if self.tournament_speed == TournamentSpeed.RAPID:
                ordered_players = queryset.order_by('lichess_rating_rapid').reverse()
                rank = 'lichess_rating_rapid'
            elif self.tournament_speed == TournamentSpeed.BLITZ:
                ordered_players = queryset.order_by('lichess_rating_blitz').reverse()
                rank = 'lichess_rating_blitz'
            elif self.tournament_speed == TournamentSpeed.CLASSICAL:
                ordered_players = queryset.order_by('lichess_rating_classical').reverse()
                rank = 'lichess_rating_classical'
            elif self.tournament_speed == TournamentSpeed.BULLET:
                ordered_players = queryset.order_by('lichess_rating_bullet').reverse()
                rank = 'lichess_rating_bullet'
            else:
                ordered_players = queryset 
        
        elif self.board_type == TournamentBoardType.OTB:
            if self.tournament_speed == TournamentSpeed.CLASSICAL:
                ordered_players = queryset.order_by('fide_rating_classical').reverse()
                rank = 'fide_rating_classical'
            else:
                ordered_players = queryset
        else:
            ordered_players = queryset
        # return {
        #     i : player
        #     for i, player in enumerate(ordered_players)
        # }
        return list(ordered_players)
    
    def getPlayersCount(self):
        return len(TournamentPlayers.objects.filter(tournament=self))
    
    def getOpponents(self):
        pass
    
    def getBuchholz(self):
        pass
    
    def getAdjustedScores(self):
        pass
    
    def getBuchholzCutMinusOne(self):
        pass
    
    def getMediamBuchholz(self):
        pass
    
    def getSonnebornBerger(self):
        pass
    
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
                count+=1
                continue
        return count

    def get_latest_round_with_games(self):
        rounds = Round.objects.filter(tournament=self)
        i = len(rounds)
        while i > 0:
            i-=1
            if len(Game.objects.filter(round=rounds[i]).filter(finished=True)) > 0:
                return rounds[i]
        return None

    def addToRankingList(self, rankingSystem: RankingSystem):
        ranking_system_obj, _ = RankingSystemClass.objects.get_or_create(value=rankingSystem)
        self.rankingList.add(ranking_system_obj)

    def getGamesCount(self, isFinished):
        return len(Round.objects.filter(tournament=self.id))

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

    players = serializers.SerializerMethodField()
    rankingList = RankingSystemClassSerializer(many=True, read_only=True)
    
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
    
    def get_players(self, obj):
        return [str(player) for player in obj.getPlayers()]
