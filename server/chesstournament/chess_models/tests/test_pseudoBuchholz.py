# crear torneo
# introducir resultado de partidas
# comprobar valor de nueva metrica en tabla rankings
# para 8 jugadores tras la segunda ronda


from django.test import TransactionTestCase, tag
from chess_models.models import Tournament, Round, Game
# from chess_mvodels.models import (
#    LichessAPIError, TournamentType, Scores)
from chess_models.models import (getScores, getRanking, getPlayers,
                                 getOpponents, getBuchholz,
                                 getAdjustedScores, getBuchholzCutMinusOne,
                                 getMediamBuchholz, getSonnebornBerger,
                                 getBlackWins)
from chess_models.models.constants import (TournamentSpeed, TournamentType,
                                           TournamentBoardType, RankingSystem)


class TournamentModelTestExtension(TransactionTestCase):
    """ test related with tournaments that
    involve the creation of games"""
    reset_sequences = True

    def setUp(self):
        from chess_models.management.commands.populate import Command
        self.command = Command()
        self.command.cleanDataBase()
        self.players = ['Fabiano', 'Nakamura', 'Nijat', 'Ian','Alireza',
                        'Praggnanandhaa', 'Gukesh', 'Vidit']

    @tag("continua")
    def test_1011_tournament_getScores(self):
        """Test function getScores that returns a list of
        players and their score for a swiss tournament"""
        win_points = 3
        draw_points = 2
        lose_points = 1
        results = {}
        results['Fabiano'] = 3.0
        results['Nakamura'] = 5.0
        results['Nijat'] = 5.0
        results['Ian'] = 3.0
        results['Alireza'] = 4.0
        results['Praggnanandhaa'] = 4.0
        results['Gukesh'] = 4.0
        results['Vidit'] = 4.0
        from chess_models.management.commands.populate import Command
        command = Command()
        command.cleanDataBase()
        command.readInputFile(
            'chess_models/management/commands/pseudo-buchholz.trf')
        command.insertData()      # Insert data into the database
        tournament_name = 'pseudo buchholz swiss'
        tournament = Tournament.objects.get(name=tournament_name)
        tournament.win_points = win_points
        tournament.draw_points = draw_points
        tournament.lose_points = lose_points
        tournament.save()
        tournament.addToRankingList(RankingSystem.PSEUDOBUCH.value)
        playersList = tournament.getPseudoBuchholz()
        score = RankingSystem.PSEUDOBUCH
        for player, points in playersList.items():
            self.assertEqual(points[score], results[player.name])
            # self.assertEqual(points['points_buchholt'],
            #                 results[player.name][1])