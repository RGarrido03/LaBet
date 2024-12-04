import datetime

from django.db import IntegrityError
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.request import Request
from rest_framework.response import Response

from app.models import Bet, Tier, User
from app.serializers import TierSerializer, UserSerializer
from app.utils.authorization import IsAuthenticatedOrNew


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
        request.user.tier.max_wallet - total_this_month,
        status=status.HTTP_200_OK,
    )


@api_view(["POST", "GET"])
@permission_classes([IsAuthenticatedOrReadOnly])
def tier(request: Request) -> Response:
    match request.method:
        case "POST":
            tier_id = request.POST["tier"]
            request.user.tier = Tier.objects.get(id=tier_id)
            request.user.save()
            return Response(
                TierSerializer(request.user.tier).data, status=status.HTTP_200_OK
            )

        case "GET":
            return Response(
                TierSerializer(Tier.objects.all(), many=True).data,
                status=status.HTTP_200_OK,
            )

        case _:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(["POST", "GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticatedOrNew])
def user(request: Request) -> Response:
    match request.method:
        case "POST":
            username = request.POST["username"]
            password = request.POST["password"]
            email = request.POST["email"]
            first_name = request.POST["first_name"]
            last_name = request.POST["last_name"]
            birth_date = request.POST["birth_date"]
            selected_tier = request.POST["selected_tier"]

            if datetime.date.fromisoformat(
                birth_date
            ) > datetime.date.today() - datetime.timedelta(days=365 * 18):
                return Response(status=status.HTTP_403_FORBIDDEN)

            try:
                user_ = User.objects.create_user(
                    username,
                    email,
                    password,
                    first_name=first_name,
                    last_name=last_name,
                    birth_date=birth_date,
                )
                user_.tier = Tier.objects.get(id=selected_tier)
                user_.save()
            except IntegrityError:
                return Response(status=status.HTTP_400_BAD_REQUEST)

        case "GET":
            return Response(
                UserSerializer(request.user).data,
                status=status.HTTP_200_OK,
            )

        case "PUT":
            try:
                for prop in request.POST:
                    if request.POST[prop]:
                        setattr(request.user, prop, request.POST[prop])
                request.user.save()
                return Response(
                    UserSerializer(request.user).data, status=status.HTTP_200_OK
                )
            except IntegrityError:
                return Response(status=status.HTTP_400_BAD_REQUEST)

        case "DELETE":
            request.user.delete()
            return Response(status=status.HTTP_200_OK)

        case _:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
