import datetime
import itertools
import json

from django.contrib.auth import authenticate, login as auth_login
from django.core.handlers.wsgi import WSGIRequest
from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import render, redirect
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.request import Request
from rest_framework.response import Response

from app.forms import LoginForm
from app.models import *
from app.serializers import (
    GameSerializer,
    BetSerializer,
    TierSerializer,
    UserSerializer,
)
from app.utils.odds import get_best_combination


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def index(request: Request) -> Response:
    games = Game.objects.all()
    already_bet_games = [
        bet.game for bet in Bet.objects.filter(user=request.user).all()
    ]

    result = [
        {"game": GameSerializer(game).data, "detail": odds}
        for game in games
        if game not in already_bet_games
        and (odds := get_best_combination(GameOdd.objects.filter(game=game).all()))
        and odds.get("odd") >= request.user.tier.min_arbitrage
    ]

    if request.user.tier.charts_included:
        # Spagehetti code, I know
        # I don't care, it works
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
            (datetime.datetime.now() - datetime.timedelta(days=30 * i)).strftime(
                "%Y-%m"
            )
            for i in range(2, -1, -1)
        ]

        data_dict = {key: (amount, profit) for key, amount, profit in chart_data}
        chart_data = [(month, *data_dict.get(month, (0, 0))) for month in months]

    return Response(
        json.dumps(
            {
                "games": result,
                "chart": (
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
                    if request.user.tier.charts_included and len(already_bet_games) > 0
                    else None
                ),
            }
        ),
        status=status.HTTP_200_OK,
    )


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
                "max_bet": request.user.tier.max_wallet - total_this_month,
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
def wallet(request: Request) -> Response:
    games = Bet.objects.filter(user=request.user).all()
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
            "games": GameSerializer(games, many=True).data,
            "remaining": request.user.tier.max_wallet - total_this_month,
            "chart": (
                {
                    "labels": [
                        f"{game.game.home_team} vs {game.game.away_team}"
                        for game in games_this_month
                    ],
                    "spent": [float(game.amount) for game in games_this_month],
                    "profit": sum(game.profit for game in games_this_month),
                }
                if len(games_this_month) > 0
                else None
            ),
        },
        status=status.HTTP_200_OK,
    )


@api_view(["POST", "GET"])
@permission_classes([IsAuthenticatedOrReadOnly])
def tier(request: Request) -> Response:
    match request.method:
        case "POST":
            tier_id = request.POST["tier"]
            request.user.tier = Tier.objects.get(id=tier_id)
            request.user.save()
            return Response(
                TierSerializer(request.user.tier).data, status=status.HTTP_200_OK
            )

        case "GET":
            return Response(
                TierSerializer(Tier.objects.all(), many=True).data,
                status=status.HTTP_200_OK,
            )

        case _:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


def login(request: WSGIRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("index")
    form = LoginForm()

    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user: User = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect("index")
        else:
            return render(
                request, "login.html", {"error": "Invalid credentials", "form": form}
            )

    return render(request, "login.html", {"form": form})


@api_view(["POST", "GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def user(request: Request) -> Response:
    match request.method:
        case "POST":
            username = request.POST["username"]
            password = request.POST["password"]
            email = request.POST["email"]
            first_name = request.POST["first_name"]
            last_name = request.POST["last_name"]
            birth_date = request.POST["birth_date"]
            selected_tier = request.POST["selected_tier"]

            if datetime.date.fromisoformat(
                birth_date
            ) > datetime.date.today() - datetime.timedelta(days=365 * 18):
                return Response(status=status.HTTP_403_FORBIDDEN)

            try:
                user_ = User.objects.create_user(
                    username,
                    email,
                    password,
                    first_name=first_name,
                    last_name=last_name,
                    birth_date=birth_date,
                )
                user_.tier = Tier.objects.get(id=selected_tier)
                user_.save()
            except IntegrityError:
                return Response(status=status.HTTP_400_BAD_REQUEST)

        case "GET":
            return Response(
                UserSerializer(request.user).data,
                status=status.HTTP_200_OK,
            )

        case "PUT":
            try:
                for prop in request.POST:
                    if request.POST[prop]:
                        setattr(request.user, prop, request.POST[prop])
                request.user.save()
                return Response(
                    UserSerializer(request.user).data, status=status.HTTP_200_OK
                )
            except IntegrityError:
                return Response(status=status.HTTP_400_BAD_REQUEST)

        case "DELETE":
            request.user.delete()
            return Response(status=status.HTTP_200_OK)

        case _:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def combinations(request: WSGIRequest) -> HttpResponse:
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
    if result.get("odd") < request.user.tier.min_arbitrage:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    return Response(json.dumps(result), status=status.HTTP_200_OK)
