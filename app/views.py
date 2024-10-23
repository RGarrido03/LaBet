from django.contrib.auth import authenticate
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect

from app.models import *
from app.modules.betclic import BetclicScrapper
from app.modules.placard import PlacardScrapper
from app.utils.odds import calculate_combinations


def index(request: WSGIRequest) -> HttpResponse:
    return render(request, "index.html")


def login(request: WSGIRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("index")

    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user: User = authenticate(request, username=username, password=password)
        if user is not None:
            return redirect("index")
        else:
            return render(request, "login.html", {"error": "Invalid credentials"})

    return render(request, "login.html")


def betclic_test(request: WSGIRequest) -> JsonResponse:
    scrapper = BetclicScrapper()
    data = scrapper.scrap()
    return JsonResponse([game_odd.to_json() for game_odd in data], safe=False)


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
