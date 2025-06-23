from collections import defaultdict
from django.shortcuts import get_object_or_404
from chess_models.models.constants import RankingSystem, Scores, TournamentBoardType, TournamentType
from chess_models.models.player import Player, PlayerSerializer
from djoser.views import UserViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, \
    IsAuthenticatedOrReadOnly
from rest_framework import status, permissions
from rest_framework.permissions import AllowAny
from chess_models.models.round import Round
from chess_models.models.tournament import Tournament, TournamentSerializer
from chess_models.models.game import Game, GameSerializer, create_rounds
from chess_models.models.other_models import LichessAPIError


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class TournamentViewSet(viewsets.ModelViewSet):
    queryset = Tournament.objects.all().order_by('-start_date', '-id')
    serializer_class = TournamentSerializer
    pagination_class = CustomPagination
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            self.permission_classes = []
        return super().get_permissions()


class CustomUserViewSet(UserViewSet):
    def create(self, request, *args, **kwargs):
        return Response({"detail": "Método no permitido."},
                        status=status.HTTP_405_METHOD_NOT_ALLOWED)


class GameViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.finished:
            return Response({'detail': 'Este juego ya está terminado.'},
                            status=status.HTTP_403_FORBIDDEN)

        response = super().update(request, *args, **kwargs)

        instance.save()

        return response


class CreateGameAPIView(APIView):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            white_id = request.data.get("white")
            black_id = request.data.get("black")
            round_id = request.data.get("round")

            if not white_id or not black_id or not round_id:
                return Response({"detail": "Missing required fields"},
                                status=status.HTTP_400_BAD_REQUEST)

            try:
                white = Player.objects.get(id=white_id)
                black = Player.objects.get(id=black_id)
            except Player.DoesNotExist:
                return Response({"detail": "Player not found"},
                                status=status.HTTP_400_BAD_REQUEST)

            round_obj, created = Round.objects.get_or_create(id=round_id)

            game = Game(white=white, black=black, round=round_obj)
            game.save()

            serializer = GameSerializer(game)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {"detail": f"Unexpected error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UpdateGameAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def patch(self, request, num):
        game = get_object_or_404(Game, id=num)

        if game.finished and not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication required "
                    "to modify a finished game."},
                status=status.HTTP_403_FORBIDDEN
            )

        partial_data = request.data.copy()
        if 'result' in partial_data:
            partial_data['finished'] = True

        serializer = GameSerializer(game, data=partial_data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateRoundAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            tournament_id = int(request.data.get('tournament_id'))
        except (TypeError, ValueError):
            return Response({"result": False},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            tournament = Tournament.objects.get(id=tournament_id)
        except Tournament.DoesNotExist:
            return Response({"result": False},
                            status=status.HTTP_400_BAD_REQUEST)

        if tournament.getPlayersCount() == 0:
            return Response({"result": False},
                            status=status.HTTP_400_BAD_REQUEST)

        create_rounds(tournament, [])

        rounds_created = tournament.round_set.count()
        games_created = tournament.getGamesCount(finished=False)

        if rounds_created == 0 or games_created == 0:
            return Response({"result": False},
                            status=status.HTTP_400_BAD_REQUEST)

        return Response({"result": True}, status=status.HTTP_201_CREATED)

class TournamentDetailAPIView(APIView):
    permission_classes = []

    def get(self, request, tournament_id):
        tournament = get_object_or_404(Tournament, id=tournament_id)
        serializer = TournamentSerializer(tournament)
        return Response(serializer.data, status=status.HTTP_200_OK)

class SearchTournamentsAPIView(APIView):
    permission_classes = []

    def get(self, request):
        tournaments = Tournament.objects.all().order_by('-name')
        serializer = TournamentSerializer(tournaments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        search_string = request.data.get('search_string')
        if not search_string:
            return Response(
                {
                    "results": False,
                    "message": "search_string is required"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        tournaments = Tournament.objects\
            .filter(name__icontains=search_string).order_by('-name')
        serializer = TournamentSerializer(tournaments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TournamentCreateAPIView(APIView):
    queryset = Tournament.objects.all()
    serializer_class = TournamentSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get(self, request):
        tournaments = Tournament.objects.all().order_by('-id')
        paginator = PageNumberPagination()
        paginator.page_size = 10
        result_page = paginator.paginate_queryset(tournaments, request)
        serializer = TournamentSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        try:
            name = request.data.get("name")
            tournament_type = request.data.get("tournament_type")
            tournament_speed = request.data.get("tournament_speed")
            board_type = request.data.get("board_type")
            players_text = request.data.get("players", "")
            start_date = request.data.get("start_date", "")

            only_admin_can_update = request.data.get(
                "only_admin_can_update", False)
            ranking_methods = request.data.get("ranking_methods", [])
            points = request.data.get("points", {})
            win_points = points.get("win", 1.0)
            draw_points = points.get("draw", 0.5)
            lose_points = points.get("loss", 0.0)

            if not all([name, tournament_type, board_type]):
                return Response(
                    {"error": "Missing required fields."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if tournament_type == 'SWISS':
                tournament_type = TournamentType.SWISS
            elif tournament_type == 'ROUNDROBIN':
                tournament_type = TournamentType.ROUNDROBIN
            
            if board_type == 'LIC':
                board_type = TournamentBoardType.LICHESS
            elif board_type == 'OTB':
                board_type = TournamentBoardType.OTB

            tournament = Tournament.objects.create(
                name=name,
                tournament_type=tournament_type,
                tournament_speed=tournament_speed,
                board_type=board_type,
                start_date=start_date,
                only_administrative=only_admin_can_update,
                win_points=win_points,
                draw_points=draw_points,
                lose_points=lose_points,
            )

            #methods: ['pseudobuchholz', 'buchholz', 'cumulative', 'wins']
            for method in ranking_methods:
                if method == 'buchholz':
                    method = RankingSystem.BUCHHOLZ
                elif method == 'cumulative':
                    method = RankingSystem.PLAIN_SCORE
                elif method == 'wins':
                    method = RankingSystem.WINS
                elif method == 'pseudobuchholz':
                    method = RankingSystem.PSEUDOBUCH
                tournament.addToRankingList(method)

            lines = players_text.strip().split("\n")
            if len(lines) > 1 and lines[0].strip()\
                    .lower() == "lichess_username":
                usernames = lines[1:]
            else:
                usernames = lines

            for username in usernames:
                Player.objects.create(
                    tournament=tournament,
                    lichess_username=username.strip()
                )

            return Response(
                {"success": True, "id": tournament.id},
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GetRanking(APIView):
    permission_classes = [AllowAny]

    def get(self, request, tournament_id, format=None):
        try:
            tournament = Tournament.objects.get(id=tournament_id)
        except Tournament.DoesNotExist:
            return Response({"detail": "Tournament not found."},
                            status=status.HTTP_404_NOT_FOUND)

        ranking = tournament.getRanking()

        systems_qs = tournament.getRankingList()
        active_systems = [entry['value']
                          for entry in systems_qs.values('value')]

        response_data = {}

        for player, data in ranking.items():
            player_data = {
                'id': player.id,
                'name': player.name,
                'score': data.get('PS', 0),
                'rank': data.get('rank')
            }

            for system in active_systems:
                if system == 'WI':
                    player_data[RankingSystem.WINS.value]\
                          = data.get('WI', 0)
                elif system == 'BT':
                    player_data[RankingSystem.BLACKTIMES.value]\
                          = data.get('BT', 0)
                elif system == 'BU':
                    player_data[RankingSystem.BUCHHOLZ.value]\
                        = data.get('BU', 0)
                else:
                    player_data[system.lower()] = data.get(system, 0)

            response_data[player.id] = player_data
        return Response(response_data, status=status.HTTP_200_OK)


class GetPlayers(APIView):
    def get(self, request, tournament_id, format=None):
        try:
            tournament = Tournament.objects.get(id=tournament_id)
        except Tournament.DoesNotExist:
            return Response({"detail": "Tournament not found."},
                            status=status.HTTP_404_NOT_FOUND)

        players = tournament.players.all()
        serializer = PlayerSerializer(players, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GetRoundResults(APIView):
    permission_classes = [AllowAny]

    def get(self, request, tournament_id, format=None):
        try:
            tournament = Tournament.objects.get(id=tournament_id)
        except Tournament.DoesNotExist:
            return Response({"detail": "Tournament not found."}, status=status.HTTP_404_NOT_FOUND)

        games = tournament.getGames()
        rounds_dict = defaultdict(list)

        for game in games:
            round_number = game.round.name
            game_data = {
                'id': game.id,
                'white': game.white.name if game.white else None,
                'black': game.black.name if game.black else None,
                'result': game.result
            }
            rounds_dict[round_number].append(game_data)

        response_data = [
            {
                "round_number": round_number,
                "games": rounds_dict[round_number]
            }
            for round_number in sorted(rounds_dict)
        ]

        return Response(response_data, status=status.HTTP_200_OK)


class UpdateLichessGameAPIView(APIView):
    permission_classes = []
    authentication_classes = []

    def post(self, request):
        game_id = request.data.get('game_id')
        lichess_game_id = request.data.get('lichess_game_id')

        if not game_id or not lichess_game_id:
            return Response(
                {"result": False, "message": "game_id and "
                    "lichess_game_id are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            game = Game.objects.get(id=game_id)
        except Game.DoesNotExist:
            return Response(
                {"result": False, "message": "Game does not exist"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if game.finished:
            return Response(
                {"result": False, "message": "Game is blocked, "
                    "only administrator can update it"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            result, white, black = game\
                .get_lichess_game_result(lichess_game_id)
        except LichessAPIError as e:
            return Response(
                {"result": False, "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST)

        game.result = result
        game.finished = True
        game.save()

        return Response({"result": True}, status=status.HTTP_200_OK)


class UpdateOTBGameAPIView(APIView):
    permission_classes = []
    authentication_classes = []

    def post(self, request, format=None):
        game_id = request.data.get('game_id')
        name = request.data.get('name')
        email = request.data.get('email')
        result = request.data.get('otb_result')

        if not all([game_id, name, email, result]):
            return Response({"result": False, "message": "Missing parameters"},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            game = Game.objects.get(id=game_id)
        except Game.DoesNotExist:
            return Response({"result": False, "message":
                             "Game does not exist"},
                            status=status.HTTP_400_BAD_REQUEST)

        if game.finished:
            return Response({"result": False, "message":
                             "Game already finished"},
                            status=status.HTTP_400_BAD_REQUEST)

        if not ((game.white.name == name and game.white.email == email) or
                (game.black.name == name and game.black.email == email)):
            return Response({"result": False, "message":
                             "Player authentication failed"},
                            status=status.HTTP_403_FORBIDDEN)

        if result not in [Scores.WHITE.value,
                          Scores.BLACK.value, Scores.DRAW.value]:
            return Response({"result": False, "message": "Invalid result"},
                            status=status.HTTP_400_BAD_REQUEST)

        game.result = result
        game.finished = True
        game.save()

        return Response({"result": True}, status=status.HTTP_200_OK)


class AdminUpdateGameAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        user = request.user
        game_id = request.data.get('game_id')
        new_result = request.data.get('otb_result')

        if not game_id or not new_result:
            return Response(
                {"result": False, "message": "Missing game_id or otb_result"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            game = Game.objects.get(id=game_id)
        except Game.DoesNotExist:
            return Response(
                {"result": False, "message": "Game not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        tournament = game.round.tournament

        if tournament.administrativeUser != user:
            return Response(
                {
                    "result": False,
                    "message": "Only the user that create "
                    "the tournament can update it"
                },
                status=status.HTTP_403_FORBIDDEN
            )

        game.result = new_result
        game.save()

        return Response(
            {"result": True, "message": "Game updated successfully"},
            status=status.HTTP_200_OK
        )
