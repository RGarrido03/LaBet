import datetime

from django.contrib.auth import authenticate, login as auth_login
from django.core.handlers.wsgi import WSGIRequest
from django.db import IntegrityError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect

from app.models import *
from app.modules.betano import BetanoScrapper
from app.modules.betclic import BetclicScrapper
from app.modules.lebull import LebullScrapper
from app.modules.placard import PlacardScrapper
from app.utils.odds import get_best_combination


def index(request: WSGIRequest) -> HttpResponse:
    if not request.user.is_authenticated:
        return render(request, "landing.html")

    games = Game.objects.all()

    result = [
        {"game": game.to_json(), "detail": odds}
        for game in games
        if (odds := get_best_combination(GameOdd.objects.filter(game=game).all()))
        and 1 > odds.get("odd") >= request.user.tier.min_arbitrage
    ]

    return render(request, "index.html", {"games": result})


def game_by_id(request: WSGIRequest, id: int) -> HttpResponse:
    if not request.user.is_authenticated:
        return redirect("index")

    id_str = str(id)

    # Since sets aren't JSON serializable, a list cast is used to store the values
    if not str(id) in request.session:
        request.session[id_str] = list()

    if request.method == "POST":
        bets = set(request.session[id_str])
        bets.add(request.POST.get("type"))
        request.session[id_str] = list(bets)
        print(request.session[id_str])
        return redirect("game_by_id", id=id)

    game = Game.objects.get(id=id)
    if not game:
        # TODO: 404 page
        return JsonResponse({"error": "Game not found"}, status=404)

    game_odds = GameOdd.objects.filter(game=game)
    if not game_odds:
        # TODO: Render error page
        return JsonResponse({"error": "No odds found for this game"}, status=404)

    odds_combination = get_best_combination(game_odds)
    odd = odds_combination.get("odd")
    max_bet = request.user.tier.max_wallet
    return render(
        request,
        "game_by_id.html",
        {
            "game": game,
            "combination": odds_combination,
            "profit": 100 * (1 - odd) if odd < 1 else 100 * (odd - 1),
            "max_bet": max_bet,
            "session": request.session[id_str],
        },
    )


def tier(request: WSGIRequest) -> HttpResponse:
    if not request.user.is_authenticated:
        return redirect("login")

    if request.method == "POST":
        tier_id = request.POST["tier"]
        request.user.tier = Tier.objects.get(id=tier_id)
        request.user.save()
        return render(request, "tier.html", {"tiers": Tier.objects.all()})
    return render(request, "tier.html", {"tiers": Tier.objects.all()})


def login(request: WSGIRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("index")

    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user: User = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect("index")
        else:
            return render(request, "login.html", {"error": "Invalid credentials"})

    return render(request, "login.html")


def register(request: WSGIRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("index")

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
                {"error": "You must be over 18 years old to register"},
            )

        try:
            User.objects.create_user(
                username,
                email,
                password,
                first_name=first_name,
                last_name=last_name,
                birth_date=birth_date,
            )
            return login(request)
        except IntegrityError:
            return render(
                request, "register.html", {"error": "Username is already taken"}
            )

    return render(request, "register.html")


def betclic_test(request: WSGIRequest) -> JsonResponse:
    # request can have a parameter to select teh date
    date_param = request.GET.get("date", None)
    date = None
    if date_param:
        date = datetime.datetime.fromisoformat(date_param)

    scrapper = BetclicScrapper()
    data = scrapper.scrap()

    if date:
        data = [game_odd.to_json() for game_odd in data if game_odd.game.date >= date]
    else:
        data = [game_odd.to_json() for game_odd in data]
    return JsonResponse(data, safe=False)


def placard_test(request: WSGIRequest) -> JsonResponse:

    scrapper = PlacardScrapper()
    data = scrapper.scrap()
    return JsonResponse([game_odd.to_json() for game_odd in data], safe=False)


def lebull_test(request: WSGIRequest) -> JsonResponse:

    scrapper = LebullScrapper()
    data = scrapper.scrap()
    return JsonResponse([game_odd.to_json() for game_odd in data], safe=False)


def betano_test(request: WSGIRequest) -> JsonResponse:

    scrapper = BetanoScrapper()
    data = scrapper.scrap()
    return JsonResponse([game_odd.to_json() for game_odd in data], safe=False)


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
