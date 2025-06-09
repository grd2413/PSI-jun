# chess_models / models / __init__ . py
from .tournament import ( Tournament, RankingSystemClass ) # noqa F401
from .other_models import Referee # noqa F401
from .round import Round # noqa F401
from .game import Game # noqa F401
from .player import Player, LichessAPIError # noqa F401
from .constants import Scores, TournamentType, TournamentSpeed, TournamentBoardType, Color, RankingSystem, LICHESS_USERS # noqa F401

getGamesCount = Tournament.getGamesCount
create_rounds = game.create_rounds
getPlayersCount = Tournament.getPlayersCount
getScores = Tournament.getScores
getRanking = Tournament.getRanking
getPlayers = Tournament.getPlayers
getOpponents = Tournament.getOpponents
getBuchholz = Tournament.getBuchholz
getAdjustedScores = Tournament.getAdjustedScores
getBuchholzCutMinusOne = Tournament.getBuchholzCutMinusOne
getMediamBuchholz = Tournament.getMediamBuchholz
getSonnebornBerger = Tournament.getSonnebornBerger
getBlackWins = Tournament.getBlackWins

# the tag noqa informs fake8 to ignore the fact that
# we are importing a method that is never used in the file

# those classes exported in __init__ . py
# may be import as
# from chess_models . models import Tournament
# instead of
# from chess_models . models . Tournament import Tournament