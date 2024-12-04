from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from app.models import Bet, Game, BetHouse
from app.serializers import GameSerializer


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def new_bet(request: Request, id: int) -> Response:
    game = Game.objects.get(id=id)
    if not game:
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
        )

    home_bet_house = BetHouse.objects.get(id=request.POST["home_bet_house"])
    draw_bet_house = BetHouse.objects.get(id=request.POST["draw_bet_house"])
    away_bet_house = BetHouse.objects.get(id=request.POST["away_bet_house"])

    if not home_bet_house or not draw_bet_house or not away_bet_house:
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
        )

    bet = Bet.objects.create(
        user=request.user,
        game=game,
        amount=request.POST["amount"],
        home_bet_house=home_bet_house,
        home_odd=request.POST["home_odd"],
        draw_bet_house=draw_bet_house,
        draw_odd=request.POST["draw_odd"],
        away_bet_house=away_bet_house,
        away_odd=request.POST["away_odd"],
    )
    return Response(
        GameSerializer(bet).data,
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def bet_games(request: Request) -> Response:
    games = Bet.objects.filter(user=request.user).all()
    return Response(
        GameSerializer(games, many=True).data,
        status=status.HTTP_200_OK,
    )
