from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from app.models import Bet
from app.serializers import BetSerializer


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def new_bet(request: Request, id: int) -> Response:
    data = request.data
    data["game"] = id
    data["user"] = request.user.id

    serialized = BetSerializer(data=request.data)
    if not serialized.is_valid():
        return Response(serialized.errors, status=status.HTTP_400_BAD_REQUEST)

    serialized.save()

    return Response(
        serialized.data,
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def bet_games(request: Request) -> Response:
    bets = Bet.objects.filter(user=request.user).all()
    return Response(
        BetSerializer(bets, many=True).data,
        status=status.HTTP_200_OK,
    )
