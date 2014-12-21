from django.contrib.auth.models import User
from rest_framework import serializers

from games.models import Game


class GameSerializer(serializers.HyperlinkedModelSerializer):

    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Game
        fields = ('url', 'code', 'owner')


class UserSerializer(serializers.HyperlinkedModelSerializer):

    games = serializers.HyperlinkedRelatedField(many=True,
                                                view_name='game-detail',
                                                read_only=True)

    class Meta:
        model = User
        fields = ('url', 'username', 'games')
