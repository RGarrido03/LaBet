import datetime
import itertools
import json

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from app.models import Bet


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def chart_history(request: Request) -> Response:
    if not request.user.tier.charts_included:
        return Response(status=status.HTTP_403_FORBIDDEN)

    already_bet_games = [
        bet.game for bet in Bet.objects.filter(user=request.user).all()
    ]

    if len(already_bet_games) == 0:
        return Response(status=status.HTTP_404_NOT_FOUND)

    chart_data = [
        (
            key,
            round(float(sum(x.amount for x in g1)), 2),
            round(float(sum(x.profit for x in g2)), 2),
        )
        for key, group in itertools.groupby(
            Bet.objects.filter(user=request.user).order_by("created_at"),
            key=lambda bet: bet.created_at.strftime("%Y-%m"),
        )
        for g1, g2 in [itertools.tee(group)]
    ]

    months = [
        (datetime.datetime.now() - datetime.timedelta(days=30 * i)).strftime("%Y-%m")
        for i in range(2, -1, -1)
    ]

    data_dict = {key: (amount, profit) for key, amount, profit in chart_data}
    chart_data = [(month, *data_dict.get(month, (0, 0))) for month in months]

    return Response(
        json.dumps(
            {
                "spent": [
                    {
                        "x": x[0],
                        "y": x[1] if x[1] != 0 else 2,
                        "meta": {"value": x[1]},
                    }
                    for x in chart_data
                ],
                "profit": [
                    {
                        "x": x[0],
                        "y": x[2] if x[2] != 0 else 2,
                        "meta": {"value": x[2]},
                    }
                    for x in chart_data
                ],
            }
        ),
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def chart_month(request: Request) -> Response:
    if not request.user.tier.charts_included:
        return Response(status=status.HTTP_403_FORBIDDEN)

    bets_this_month = (
        Bet.objects.filter(
            user=request.user, created_at__month=datetime.datetime.now().month
        )
        .order_by("created_at")
        .all()
    )

    if len(bets_this_month) == 0:
        return Response(status=status.HTTP_404_NOT_FOUND)

    return Response(
        json.dumps(
            {
                "labels": [
                    f"{bet.game.home_team} vs {bet.game.away_team}"
                    for bet in bets_this_month
                ],
                "spent": [float(bet.amount) for bet in bets_this_month],
                "profit": sum(bet.profit for bet in bets_this_month),
            }
        ),
        status=status.HTTP_200_OK,
    )
