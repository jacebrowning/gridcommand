from django.contrib.auth.models import User
from rest_framework import serializers

from games.models import Game, Player


class GameSerializer(serializers.HyperlinkedModelSerializer):

    owner = serializers.ReadOnlyField(source='owner.username')
    players = serializers.HyperlinkedRelatedField(
        view_name='player-detail',
        many=True,
        read_only=True,
    )

    class Meta:
        model = Game
        fields = ('url', 'code', 'owner', 'players')


class UserSerializer(serializers.HyperlinkedModelSerializer):

    games = serializers.HyperlinkedRelatedField(
        view_name='game-detail',
        many=True,
        read_only=True,
    )

    class Meta:
        model = User
        fields = ('url', 'username', 'games')


class PlayerSerializer(serializers.HyperlinkedModelSerializer):

    game = serializers.HyperlinkedRelatedField(
        view_name='game-detail',
        read_only=True,
    )

    class Meta:
        model = Player
        fields = ('url', 'color', 'game')
