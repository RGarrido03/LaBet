import datetime
import json

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

import app.views.user
from app.models import *
from app.serializers import (
    GameSerializer,
    BetSerializer,
)
from app.utils.odds import get_best_combination


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def game_by_id(request: Request, id: int) -> Response:
    game = Game.objects.get(id=id)
    if not game:
        return Response(
            status=status.HTTP_404_NOT_FOUND,
        )

    game_odds = GameOdd.objects.filter(game=game).all()
    odds_combination = get_best_combination(game_odds)

    id_str = str(id)
    if not str(id) in request.session:
        request.session[id_str] = {}

    if request.method == "POST":
        # Update session
        request.session[id_str][request.POST.get("type")] = float(
            request.POST.get("odd")
        )
        request.session[id_str]["total"] = float(request.POST.get("total"))
        request.session.modified = True

        if all(
            [otype in request.session[id_str] for otype in ["home", "draw", "away"]]
        ):
            # Submit the bet
            bet = Bet.objects.create(
                user=request.user,
                game=game,
                home_bet_house=odds_combination["home"]["house"],
                home_odd=request.session[id_str]["home"],
                draw_bet_house=odds_combination["draw"]["house"],
                draw_odd=request.session[id_str]["draw"],
                away_bet_house=odds_combination["away"]["house"],
                away_odd=request.session[id_str]["away"],
                amount=request.POST.get("total"),
            )
            return Response(BetSerializer(bet).data, status=status.HTTP_201_CREATED)

        return Response(status=status.HTTP_200_OK)

    for key in request.session[id_str]:
        if key in ["home", "draw", "away"]:
            odds_combination[key]["odd"] = request.session[id_str][key]

    games_this_month = (
        Bet.objects.filter(
            user=request.user, created_at__month=datetime.datetime.now().month
        )
        .order_by("created_at")
        .all()
    )
    total_this_month = sum([game.amount for game in games_this_month])

    return Response(
        json.dumps(
            {
                "game": GameSerializer(game).data,
                "combination": odds_combination,
                "profit": (
                    100 * (1 - odd)
                    if (odd := odds_combination.get("odd")) < 1
                    else 100 * (odd - 1)
                ),
                "max_bet": app.views.game.user.tier.max_wallet - total_this_month,
                "session": request.session[id_str],
                "submitted": all(
                    [
                        otype in request.session[id_str]
                        for otype in ["home", "draw", "away"]
                    ]
                ),
            },
        ),
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def bet_games(request: Request) -> Response:
    games = Bet.objects.filter(user=request.user).all()

    return Response(
        GameSerializer(games, many=True).data,
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def combinations(request: Request) -> Response:
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
        and odds.get("odd") >= app.views.game.user.tier.min_arbitrage
    ]

    return Response(json.dumps(result), status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def combinations_by_id(request: Request, id: int) -> Response:
    game = Game.objects.get(id=id)
    if not game:
        return Response(status=status.HTTP_404_NOT_FOUND)

    game_odds = GameOdd.objects.filter(game=game)
    if not game_odds:
        return Response(status=status.HTTP_404_NOT_FOUND)

    result = get_best_combination(list(game_odds))
    if result.get("odd") < app.views.game.user.tier.min_arbitrage:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    return Response(json.dumps(result), status=status.HTTP_200_OK)
