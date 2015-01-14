from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework import permissions

from games.models import Game
from games.serializers import GameSerializer, UserSerializer
from games.permissions import IsOwnerOrReadOnly


class GameViewSet(viewsets.ModelViewSet):

    """This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions."""

    queryset = Game.objects.all()
    serializer_class = GameSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly)

    def perform_create(self, serializer):
            serializer.save(owner=self.request.user)


class UserViewSet(viewsets.ReadOnlyModelViewSet):

    """This viewset automatically provides `list` and `detail` actions."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
