from django.contrib.auth.models import User
from rest_framework import serializers

from games.models import Game


class GameSerializer(serializers.ModelSerializer):

    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Game
        fields = ('id', 'code', 'owner')


class UserSerializer(serializers.ModelSerializer):

    games = serializers.PrimaryKeyRelatedField(many=True,
                                               queryset=Game.objects.all())

    class Meta:
        model = User
        fields = ('id', 'username', 'games')
