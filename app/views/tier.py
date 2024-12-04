from drf_yasg.openapi import Parameter
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from app.models import Tier
from app.serializers import TierSerializer


@swagger_auto_schema(method="GET", responses={200: TierSerializer(many=True)})
@api_view(["GET"])
def tier(_: Request) -> Response:
    return Response(
        TierSerializer(Tier.objects.all(), many=True).data,
        status=status.HTTP_200_OK,
    )


@swagger_auto_schema(
    method="POST",
    manual_parameters=[Parameter("tier", in_="query", type="integer")],
    responses={200: TierSerializer()},
)
@swagger_auto_schema(method="GET", responses={200: TierSerializer()})
@api_view(["POST", "GET"])
@permission_classes([IsAuthenticated])
def tier_me(request: Request) -> Response:
    if request.method == "POST":
        tier_id = request.POST["id"]

        try:
            tier = Tier.objects.get(id=tier_id)
        except Tier.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        request.user.tier = tier
        request.user.save()

    return Response(TierSerializer(request.user.tier).data, status=status.HTTP_200_OK)
