import datetime
import itertools

from django.contrib.auth import authenticate, login as auth_login
from django.core.handlers.wsgi import WSGIRequest
from django.db import IntegrityError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect

from app.forms import LoginForm, SignupForm, ProfileForm
from app.models import *
from app.utils.odds import get_best_combination


def index(request: WSGIRequest) -> HttpResponse:
    if not request.user.is_authenticated:
        return render(request, "landing.html")

    games = Game.objects.all()
    already_bet_games = [
        bet.game for bet in Bet.objects.filter(user=request.user).all()
    ]

    result = [
        {"game": game.to_json(), "detail": odds}
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

    return render(
        request,
        "index.html",
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
        },
    )


def game_by_id(request: WSGIRequest, id: int) -> HttpResponse:
    if not request.user.is_authenticated:
        return redirect("index")

    game = Game.objects.get(id=id)
    if not game:
        # TODO: 404 page
        return JsonResponse({"error": "Game not found"}, status=404)

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
            Bet.objects.create(
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

        # Prevent the form from being submitted twice upon browser refresh

        return redirect("game_by_id", id=id)

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

    return render(
        request,
        "game_by_id.html",
        {
            "game": game,
            "combination": odds_combination,
            "profit": (
                100 * (1 - odd)
                if (odd := odds_combination.get("odd")) < 1
                else 100 * (odd - 1)
            ),
            "max_bet": request.user.tier.max_wallet - total_this_month,
            "session": request.session[id_str],
            "submitted": all(
                [otype in request.session[id_str] for otype in ["home", "draw", "away"]]
            ),
        },
    )


def wallet(request: WSGIRequest) -> HttpResponse:
    if not request.user.is_authenticated:
        return redirect("login")

    games = Bet.objects.filter(user=request.user).all()
    games_this_month = (
        Bet.objects.filter(
            user=request.user, created_at__month=datetime.datetime.now().month
        )
        .order_by("created_at")
        .all()
    )
    total_this_month = sum([game.amount for game in games_this_month])

    return render(
        request,
        "wallet.html",
        {
            "games": games,
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
    )


def tier(request: WSGIRequest) -> HttpResponse:
    # FIXME RUBEN, see this please
    # removi pq temos de poder aceder aos tiers sem estar logado para o user saber ao que vai

    # if not request.user.is_authenticated:
    #     return redirect("login")
    response = render(request, "tier.html", {"tiers": Tier.objects.all()})

    if request.method == "POST":
        tier_id = request.POST["tier"]
        if request.user.is_authenticated:
            request.user.tier = Tier.objects.get(id=tier_id)
            request.user.save()

    return render(request, "tier.html", {"tiers": Tier.objects.all()})


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


def profile(request: WSGIRequest) -> HttpResponse:
    if not request.user.is_authenticated:
        return redirect("login")

    form = ProfileForm(user=request.user)

    if request.method == "POST":
        try:
            for prop in request.POST:

                if request.POST[prop]:
                    print("prop", prop)
                    setattr(request.user, prop, request.POST[prop])

            request.user.save()

            return redirect("index")
        except IntegrityError:
            return render(
                request,
                "register.html",
                {"error": "Username is already taken", "form": form},
            )

    return render(request, "profile.html", {"form": form})


def about(request: WSGIRequest) -> HttpResponse:
    return render(request, "about.html")


def register(request: WSGIRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("index")
    form = SignupForm()
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        email = request.POST["email"]
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        birth_date = request.POST["birth_date"]

        if datetime.date.fromisoformat(
            birth_date
        ) > datetime.date.today() - datetime.timedelta(days=365 * 18):
            return render(
                request,
                "register.html",
                {"error": "You must be over 18 years old to register", "form": form},
            )

        try:
            user = User.objects.create_user(
                username,
                email,
                password,
                first_name=first_name,
                last_name=last_name,
                birth_date=birth_date,
            )
            selected_tier = request.COOKIES.get("selected_tier")
            if selected_tier:
                try:
                    tier_ = Tier.objects.get(id=selected_tier)
                    user.tier = tier_
                    user.save()
                    # delete cookie
                    request.COOKIES.pop("selected_tier")
                except Tier.DoesNotExist:
                    pass
            else:
                # redirect to tier selection page
                user.save()
                login(request)
                response = redirect("tier")
                return response

            return login(request)
        except IntegrityError:
            return render(
                request,
                "register.html",
                {"error": "Username is already taken", "form": form},
            )

    return render(request, "register.html", {"form": form})


def combinations(request: WSGIRequest) -> HttpResponse:
    debug = request.GET.get("debug", True)
    games = Game.objects.all()

    result = [
        {"game": game.to_json(), "detail": game_odds}
        for game in games
        if (
            game_odds := get_best_combination(
                GameOdd.objects.filter(game=game).all(), debug=debug
            )
        )
        and game_odds.get("odd") < 1
    ]

    return JsonResponse(result, safe=False)


def combinations_by_id(request: WSGIRequest, id: int) -> HttpResponse:
    debug = request.GET.get("debug", False)
    game = Game.objects.get(id=id)
    if not game:
        return JsonResponse({"error": "Game not found"}, status=404)

    game_odds = GameOdd.objects.filter(game=game)
    if not game_odds:
        return JsonResponse({"error": "No odds found for this game"}, status=404)

    result = get_best_combination(game_odds, debug=debug)

    return JsonResponse(result, safe=False)
