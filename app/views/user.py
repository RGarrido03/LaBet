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

from app.models import Bet, Tier, User
from app.serializers import UserSerializer, UserCreateSerializer
from app.utils.authorization import IsAdmin, IsAuthenticatedOrNew, IsAdminOrNew
from app.utils.type_conversion import str_to_bool


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
@swagger_auto_schema(method="GET", responses={200: UserSerializer(many=True)})
@api_view(["POST", "GET"])
@permission_classes([IsAuthenticatedOrNew, IsAdminOrNew])
def new_user(request: Request) -> Response:
    match request.method:
        case "POST":
            serialized = UserCreateSerializer(data=request.data)
            serialized.is_valid(raise_exception=True)
            tier = request.POST["tier"] if "tier" in request.POST else 1

            try:
                user_ = serialized.save()
                user_.tier = Tier.objects.get(id=tier)
                user_.save()
                return Response(
                    UserSerializer(user_).data, status=status.HTTP_201_CREATED
                )
            except IntegrityError:
                return Response(status=status.HTTP_400_BAD_REQUEST)

        case "GET":
            users = User.objects.all()
            return Response(
                UserSerializer(users, many=True).data, status=status.HTTP_200_OK
            )

        case _:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


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


def change_user_prop(request: Request, id: int, prop: str) -> Response:
    try:
        new_state = str_to_bool(request.GET.get("new_state", None))
    except ValueError:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.filter(id=id).first()
    if not user:
        return Response(status=status.HTTP_404_NOT_FOUND)
    setattr(user, prop, new_state)
    user.save()
    return Response(UserSerializer(user).data, status=status.HTTP_200_OK)


@swagger_auto_schema(method="PATCH", responses={200: UserSerializer()})
@api_view(["PATCH"])
@permission_classes([IsAuthenticated, IsAdmin])
def change_user_state(request: Request, id: int) -> Response:
    return change_user_prop(request, id, "is_active")


@swagger_auto_schema(method="PATCH", responses={200: UserSerializer()})
@api_view(["PATCH"])
@permission_classes([IsAuthenticated, IsAdmin])
def change_user_admin(request: Request, id: int) -> Response:
    return change_user_prop(request, id, "is_superuser")


@swagger_auto_schema(method="GET", responses={200: UserSerializer(), 404: "Not found"})
@swagger_auto_schema(
    method="PUT", request_body=UserSerializer(), responses={200: UserSerializer()}
)
@api_view(["GET", "PUT"])
@permission_classes([IsAuthenticated, IsAdmin])
def get_or_update_user(request: Request, id: int) -> Response:
    match request.method:
        case "GET":
            user = User.objects.filter(id=id).first()
            if not user:
                return Response(status=status.HTTP_404_NOT_FOUND)
            return Response(UserSerializer(user).data, status=status.HTTP_200_OK)

        case "PUT":
            user = User.objects.filter(id=id).first()
            if not user:
                return Response(status=status.HTTP_404_NOT_FOUND)

            serialized = UserSerializer(user, data=request.data)
            if not serialized.is_valid():
                return Response(serialized.errors, status=status.HTTP_400_BAD_REQUEST)
            serialized.save()
            return Response(serialized.data, status=status.HTTP_200_OK)

        case _:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


@swagger_auto_schema(
    method="PATCH",
    responses={200: UserSerializer(), 404: "Not found", 400: "Tier ID is required"},
)
@api_view(["PATCH"])
@permission_classes([IsAuthenticated, IsAdmin])
def change_user_tier(request: Request, id: int) -> Response:
    tier_id = request.GET.get("tier", None)
    if tier_id is None:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    tier = Tier.objects.filter(id=tier_id).first()
    if not tier:
        return Response(status=status.HTTP_404_NOT_FOUND)

    user = User.objects.filter(id=id).first()
    if not user:
        return Response(status=status.HTTP_404_NOT_FOUND)

    user.tier = tier
    user.save()
    return Response(UserSerializer(user).data, status=status.HTTP_200_OK)
