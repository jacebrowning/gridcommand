from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework import permissions

from games.models import Game
from games.serializers import GameSerializer, UserSerializer
from games.permissions import IsOwnerOrReadOnly


class GameList(generics.ListCreateAPIView):

    """List all games, or create a new game."""

    queryset = Game.objects.all()
    serializer_class = GameSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class GameDetail(generics.RetrieveUpdateDestroyAPIView):

    """Retrieve, update or delete a game instance."""

    queryset = Game.objects.all()
    serializer_class = GameSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly)


class UserList(generics.ListAPIView):

    """List all users."""

    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetail(generics.RetrieveAPIView):

    """Retrieve a user instance."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
