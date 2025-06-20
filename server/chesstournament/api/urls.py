from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CreateGameAPIView,
    TournamentViewSet,
    CustomUserViewSet,
    GameViewSet,
    CreateRoundAPIView,
    SearchTournamentsAPIView,
    TournamentCreateAPIView,
    GetRanking,
    GetPlayers,
    GetRoundResults,
    UpdateGameAPIView,
    UpdateLichessGameAPIView,
    UpdateOTBGameAPIView,
    AdminUpdateGameAPIView,
)

router = DefaultRouter()
router.register(r'tournament', TournamentViewSet, basename='tournament')
router.register(r'users', CustomUserViewSet, basename='users')
router.register(r'game', GameViewSet, basename='game')

urlpatterns = [
    path('', include(router.urls)),
    
    # Endpoints adicionales
    path('create_round/', CreateRoundAPIView.as_view(), name='create_round'),
    path('searchTournaments/', SearchTournamentsAPIView.as_view(), name='search_tournaments'),
    path('games/', CreateGameAPIView.as_view(), name='create-game'),
    path('games/<int:num>/', UpdateGameAPIView.as_view(), name='update_game'),
    path('tournaments/', TournamentCreateAPIView.as_view(), name='tournament_create'),
    path('get_ranking/<int:tournament_id>/', GetRanking.as_view(), name='get_ranking'),
    path('get_players/<int:tournament_id>/', GetPlayers.as_view(), name='get_players'),
    path('get_round_results/<int:tournament_id>/', GetRoundResults.as_view(), name='get_round_results'),
    path('update_lichess_game/', UpdateLichessGameAPIView.as_view(), name='update_lichess_game'),
    path('update_otb_game/', UpdateOTBGameAPIView.as_view(), name='update_otb_game'),
    path('admin_update_game/', AdminUpdateGameAPIView.as_view(), name='admin_update_game'),
]
