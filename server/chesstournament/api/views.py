from django.shortcuts import get_object_or_404
from chess_models.models.player import Player
import djoser
from djoser.views import UserViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
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
            self.permission_classes = [] #Permitir sin login
        return super().get_permissions()

class CustomUserViewSet(UserViewSet):
    def create(self, request, *args, **kwargs):
        # Devolver un 405 Method Not Allowed al intentar crear un usuario
        return Response({"detail": "Método no permitido."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

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
    permission_classes = [IsAuthenticatedOrReadOnly]

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            white_id = request.data.get("white")
            black_id = request.data.get("black")
            round_id = request.data.get("round")

            if not white_id or not black_id or not round_id:
                return Response({"detail": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

            try:
                white = Player.objects.get(id=white_id)
                black = Player.objects.get(id=black_id)
            except Player.DoesNotExist:
                return Response({"detail": "Player not found"}, status=status.HTTP_400_BAD_REQUEST)

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
                {"detail": "Authentication required to modify a finished game."},
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
            return Response({"result": False}, status=status.HTTP_400_BAD_REQUEST)

        try:
            tournament = Tournament.objects.get(id=tournament_id)
        except Tournament.DoesNotExist:
            return Response({"result": False}, status=status.HTTP_400_BAD_REQUEST)

        if tournament.getPlayersCount() == 0:
            return Response({"result": False}, status=status.HTTP_400_BAD_REQUEST)

        create_rounds(tournament, [])

        rounds_created = tournament.round_set.count()
        games_created = tournament.getGamesCount(finished=False)

        if rounds_created == 0 or games_created == 0:
            return Response({"result": False}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"result": True}, status=status.HTTP_201_CREATED)

    # def post(self, request):
    #     # Obtenemos el tournament_id de los datos de la petición
    #     try:
    #         tournament_id = int(request.data.get('tournament_id'))
    #     except (TypeError, ValueError):
    #         return Response({"result": False}, status=status.HTTP_400_BAD_REQUEST)

    #     # Se intenta obtener el torneo, si no existe se responde con error
    #     try:
    #         tournament = Tournament.objects.get(id=tournament_id)
    #     except Tournament.DoesNotExist:
    #         return Response({"result": False}, status=status.HTTP_400_BAD_REQUEST)

    #     # Validamos que el torneo tenga jugadores registrados
    #     if tournament.getPlayersCount() == 0:
    #         return Response({"result": False}, status=status.HTTP_400_BAD_REQUEST)

    #     # Llamada a la función para crear rondas y juegos
    #     create_rounds(tournament, [])

    #     # Verificar que se hayan creado rondas y juegos exitosamente.
    #     # Aquí se debe implementar la validación correspondiente. Ejemplo:
    #     if not tournament.rounds.exists():
    #         return Response({"result": False}, status=status.HTTP_400_BAD_REQUEST)

    #     return Response({"result": True}, status=status.HTTP_201_CREATED)

class SearchTournamentsAPIView(APIView):
    permission_classes = []

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

        tournaments = Tournament.objects.filter(name__icontains=search_string).order_by('-name') 
        serializer = TournamentSerializer(tournaments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class TournamentCreateAPIView(APIView):
    queryset = Tournament.objects.all()
    serializer_class = TournamentSerializer
    #permission_classes = [permissions.IsAuthenticated]
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

            if not all([name, tournament_type, tournament_speed, board_type]):
                return Response(
                    {"error": "Missing required fields."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            tournament = Tournament.objects.create(
                name=name,
                tournament_type=tournament_type,
                tournament_speed=tournament_speed,
                board_type=board_type,
                start_date=start_date,
            )

            lines = players_text.strip().split("\n")
            if len(lines) > 1 and lines[0].strip().lower() == "lichess_username":
                usernames = lines[1:]
            else:
                usernames = lines

            for username in usernames:
                Player.objects.create(
                    tournament=tournament,
                    lichess_username=username.strip()
                )

            return Response(
                {"success": True, "tournament_id": tournament.id},
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
class GetRanking(APIView):
    def get(self, request, tournament_id, format=None):

        return Response({"detail": "Not implemented"}, status=status.HTTP_501_NOT_IMPLEMENTED)

class GetPlayers(APIView):
    def get(self, request, tournament_id, format=None):

        return Response({"detail": "Not implemented"}, status=status.HTTP_501_NOT_IMPLEMENTED)

class GetRoundResults(APIView):
    def get(self, request, tournament_id, format=None):

        return Response({"detail": "Not implemented"}, status=status.HTTP_501_NOT_IMPLEMENTED)

class UpdateLichessGameAPIView(APIView):
    permission_classes = []  # Sin restricciones de permisos
    authentication_classes = []  # Desactiva la autenticación

    def post(self, request):
        game_id = request.data.get('game_id')
        lichess_game_id = request.data.get('lichess_game_id')

        # Validar que se envíen los identificadores necesarios
        if not game_id or not lichess_game_id:
            return Response(
                {"result": False, "message": "game_id and lichess_game_id are required"},
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
                {"result": False, "message": "Game is blocked, only administrator can update it"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Se conecta a Lichess y obtiene el resultado
        try:
            winner, white, black = game.get_lichess_game_result(lichess_game_id)
        except LichessAPIError as e:
            return Response(
                {"result": False, "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Se actualiza el juego con el resultado obtenido
        game.result = winner
        game.finished = True
        game.save()

        return Response({"result": True}, status=status.HTTP_200_OK)

class UpdateOTBGameAPIView(APIView):
    def put(self, request, format=None):

        return Response({"detail": "Not implemented"}, status=status.HTTP_501_NOT_IMPLEMENTED)

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
                    "message": "Only the user that create the tournament can update it"
                },
                status=status.HTTP_403_FORBIDDEN
            )

        game.result = new_result
        game.save()

        return Response(
            {"result": True, "message": "Game updated successfully"},
            status=status.HTTP_200_OK
        )