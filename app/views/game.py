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

    # if in the get parameter there is a bet keyword, then we will return the bet with that id
    is_bet = request.GET.get("bet", None)

    count_people_betting = Bet.objects.filter(game=game).count()



    return Response(
        {
            "game": GameSerializer(game).data,
            "detail": combination,
            "profit": profit,
            "max_bet": request.user.tier.max_wallet - total_this_month,
            "" if is_bet else "bet": Bet.objects.filter(user=request.user, game=game).first(),
            "count_people_betting": count_people_betting
,
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

    name_to_filter = request.GET.get("name")
    odd_to_filter = request.GET.get("odd")
    filter_type = request.GET.get("filter_type")  # gt or lt
    sort_way = request.GET.get("sort") # ASC OR DESC




    result = [
        {"game": GameSerializer(game).data, "detail": odds}
        for game in games
        if game not in already_bet_games
        and (
            odds := get_best_combination(list(GameOdd.objects.filter(game=game).all()))
        )
        and odds.get("odd") >= request.user.tier.min_arbitrage
    ]
    # Do the filter thing with the result
    from pprint import pprint
    pprint(result)


    if name_to_filter:
        result = [game for game in result if name_to_filter.lower() in game["game"]["home_team"]["name"].lower() or name_to_filter.lower() in game["game"]["away_team"]["name"].lower()]

    if odd_to_filter:
        if filter_type == "gt":
            result = [game for game in result if game["detail"]["odd"] > float(odd_to_filter)]
        elif filter_type == "lt":
            result = [game for game in result if game["detail"]["odd"] < float(odd_to_filter)]

    if sort_way == "ASC":
        result = sorted(result, key=lambda x: x["detail"]["odd"])
    elif sort_way == "DESC":
        result = sorted(result, key=lambda x: -x["detail"]["odd"])


    return Response(result, status=status.HTTP_200_OK)
