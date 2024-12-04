import datetime

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from app.models import *
from app.serializers import (
    GameSerializer,
)
from app.utils.odds import get_best_combination


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def game_by_id(request: Request, id: int) -> Response:
    game = Game.objects.get(id=id)
    if not game:
        return Response(
            status=status.HTTP_404_NOT_FOUND,
        )

    game_odds = GameOdd.objects.filter(game=game).all()
    if not game_odds:
        return Response(status=status.HTTP_404_NOT_FOUND)

    combination = get_best_combination(list(game_odds))
    if not combination:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if combination.get("odd") < request.user.tier.min_arbitrage:
        return Response(status=status.HTTP_403_FORBIDDEN)

    profit = (
        100 * (1 - combination.get("odd")) * 1 if combination.get("odd") < 1 else -1
    )

    games_this_month = (
        Bet.objects.filter(
            user=request.user, created_at__month=datetime.datetime.now().month
        )
        .order_by("created_at")
        .all()
    )
    total_this_month = sum([game.amount for game in games_this_month])

    return Response(
        {
            "game": GameSerializer(game).data,
            "combination": combination,
            "profit": profit,
            "max_bet": request.user.tier.max_wallet - total_this_month,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def games(request: Request) -> Response:
    games = Game.objects.all()

    already_bet_games = [
        bet.game for bet in Bet.objects.filter(user=request.user).all()
    ]

    result = [
        {"game": GameSerializer(game).data, "detail": odds}
        for game in games
        if game not in already_bet_games
        and (
            odds := get_best_combination(list(GameOdd.objects.filter(game=game).all()))
        )
        and odds.get("odd") >= request.user.tier.min_arbitrage
    ]

    return Response(result, status=status.HTTP_200_OK)
