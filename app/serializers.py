from rest_framework import serializers

from app.models import *


class TierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tier
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "tier",
            "birth_date",
            "iban",
        )


class SportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sport
        fields = "__all__"


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = "__all__"


class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = "__all__"


class BetHouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = BetHouse
        fields = "__all__"


class GameOddSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameOdd
        fields = "__all__"


class BetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bet
        fields = "__all__"
