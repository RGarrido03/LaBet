from rest_framework import serializers

from app.models import *


class BaseSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"


class TierSerializer(BaseSerializer):
    class Meta:
        model = Tier


class UserSerializer(BaseSerializer):
    class Meta:
        model = User


class SportSerializer(BaseSerializer):
    class Meta:
        model = Sport


class TeamSerializer(BaseSerializer):
    class Meta:
        model = Team


class GameSerializer(BaseSerializer):
    class Meta:
        model = Game


class BetHouseSerializer(BaseSerializer):
    class Meta:
        model = BetHouse


class GameOddSerializer(BaseSerializer):
    class Meta:
        model = GameOdd


class BetSerializer(BaseSerializer):
    class Meta:
        model = Bet
