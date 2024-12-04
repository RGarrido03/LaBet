from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from app.models import Bet
from app.serializers import GameSerializer


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def bet_games(request: Request) -> Response:
    games = Bet.objects.filter(user=request.user).all()

    return Response(
        GameSerializer(games, many=True).data,
        status=status.HTTP_200_OK,
    )
