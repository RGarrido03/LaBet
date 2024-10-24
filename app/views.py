import datetime

from django.contrib.auth import authenticate, login as auth_login
from django.core.handlers.wsgi import WSGIRequest
from django.db import IntegrityError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect

from app.models import *
from app.modules.betclic import BetclicScrapper
from app.modules.placard import PlacardScrapper
from app.utils.odds import calculate_combinations


def index(request: WSGIRequest) -> HttpResponse:
    return render(request, "index.html")


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
    #request can have a parameter to select teh date
    date_param = request.GET.get('date', None)
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


def combinations(request: WSGIRequest, id: int) -> HttpResponse:
    game = Game.objects.get(id=id)
    if not game:
        return JsonResponse({"error": "Game not found"}, status=404)

    game_odds = GameOdd.objects.filter(game=game)
    if not game_odds:
        return JsonResponse({"error": "No odds found for this game"}, status=404)

    result = calculate_combinations(game_odds)

    return JsonResponse(result, safe=False)
