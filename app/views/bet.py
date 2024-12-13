from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from app.models import Bet
from app.serializers import BetSerializer


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_bet_by_id(request: Request, id: int) -> Response:
    try:
        bet = Bet.objects.filter(user=request.user, id=id).get()
    except Bet.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    return Response(
        BetSerializer(bet).data,
        status=status.HTTP_200_OK,
    )


@api_view(["POST", "GET"])
@permission_classes([IsAuthenticated])
def bet_games(request: Request) -> Response:
    match request.method:
        case "POST":
            data = request.data
            data["user"] = request.user.id

            serialized = BetSerializer(data=request.data)
            if not serialized.is_valid():
                return Response(serialized.errors, status=status.HTTP_400_BAD_REQUEST)

            serialized.save()

            return Response(
                serialized.data,
                status=status.HTTP_201_CREATED,
            )
        case "GET":
            bets = Bet.objects.filter(user=request.user).all()
            return Response(
                BetSerializer(bets, many=True).data,
                status=status.HTTP_200_OK,
            )
        case _:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)



