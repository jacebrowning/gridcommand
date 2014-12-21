from rest_framework import generics

from games.models import Game
from games.serializers import GameSerializer


class GameList(generics.ListCreateAPIView):

    """List all games, or create a new game."""

    queryset = Game.objects.all()
    serializer_class = GameSerializer


class GameDetail(generics.RetrieveUpdateDestroyAPIView):

    """Retrieve, update or delete a game instance."""

    queryset = Game.objects.all()
    serializer_class = GameSerializer
