import datetime

from django.db import IntegrityError
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import (
    api_view,
    permission_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from app.models import Bet, Tier
from app.serializers import UserSerializer, UserCreateSerializer


@swagger_auto_schema(method="GET", responses={200: "Wallet"})
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def wallet(request: Request) -> Response:
    games_this_month = (
        Bet.objects.filter(
            user=request.user, created_at__month=datetime.datetime.now().month
        )
        .order_by("created_at")
        .all()
    )
    total_this_month = sum([game.amount for game in games_this_month])

    return Response(
        {"remaining": request.user.tier.max_wallet - total_this_month},
        status=status.HTTP_200_OK,
    )


@swagger_auto_schema(
    method="POST",
    request_body=UserSerializer,
    responses={201: UserSerializer(), 400: "Already exists", 403: "Too young (18+)"},
)
@api_view(["POST"])
def new_user(request: Request) -> Response:
    if request.method != "POST":
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    serialized = UserCreateSerializer(data=request.data)
    serialized.is_valid(raise_exception=True)
    tier = request.POST["tier"] if "tier" in request.POST else 1

    if serialized.validated_data[
        "birth_date"
    ] > datetime.date.today() - datetime.timedelta(days=365 * 18):
        return Response(
            {"birth_date": ["You must be at least 18 years old"]},
            status=status.HTTP_403_FORBIDDEN,
        )

    try:
        user_ = serialized.save()
        user_.tier = Tier.objects.get(id=tier)
        user_.save()
        return Response(UserSerializer(user_).data, status=status.HTTP_201_CREATED)
    except IntegrityError:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(method="GET", responses={200: UserSerializer()})
@swagger_auto_schema(
    method="PUT", request_body=UserSerializer, responses={200: UserSerializer()}
)
@swagger_auto_schema(method="DELETE", responses={200: "Deleted"})
@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def user_me(request: Request) -> Response:
    match request.method:
        case "GET":
            return Response(
                UserSerializer(request.user).data,
                status=status.HTTP_200_OK,
            )

        case "PUT":
            serialized = UserSerializer(request.user, data=request.data)
            if not serialized.is_valid():
                return Response(serialized.errors, status=status.HTTP_400_BAD_REQUEST)
            serialized.save()
            return Response(serialized.data, status=status.HTTP_200_OK)

        case "DELETE":
            request.user.delete()
            return Response(status=status.HTTP_200_OK)

        case _:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
