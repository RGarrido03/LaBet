import json

from django.core import serializers
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from app.modules.betclic import BetclicScrapper


def index(request: WSGIRequest) -> HttpResponse:
    return render(request, "index.html")


def scrap_test(request: WSGIRequest) -> JsonResponse:
    scrapper = BetclicScrapper()
    data = scrapper.scrap()
    return JsonResponse([game_odd.to_json() for game_odd in data], safe=False)