from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from app.models import *


class TierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tier
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    tier = TierSerializer(read_only=True)

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
            "is_superuser",
            "is_active",
        )


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        validated_data["password"] = make_password(validated_data["password"])
        return super().create(validated_data)

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "tier",
            "birth_date",
            "password",
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
    home_team = TeamSerializer(read_only=True)
    away_team = TeamSerializer(read_only=True)

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


class BetBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bet
        fields = "__all__"


class BetSerializerWithoutNested(BetBaseSerializer):
    profit = serializers.ReadOnlyField()
    home_bet_house = BetHouseSerializer(read_only=True)
    draw_bet_house = BetHouseSerializer(read_only=True)
    away_bet_house = BetHouseSerializer(read_only=True)


class BetSerializer(BetSerializerWithoutNested):
    game = GameSerializer(read_only=True)
    user = UserSerializer(read_only=True)
