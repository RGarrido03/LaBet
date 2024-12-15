from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from app.models import Game, Team
from app.serializers import GameSerializer, TeamSerializer


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_games_per_team(request: Request, team_id: int) -> Response:
    team = Team.objects.filter(id=team_id).first()
    if not team:
        return Response({"error": "Team not found"}, status=404)

    home_games = Game.objects.filter(home_team=team)
    away_games = Game.objects.filter(away_team=team)
    games = home_games.union(away_games)

    serialized_games = GameSerializer(games, many=True)
    return Response(serialized_games.data, status=200)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_team(request: Request, team_id) -> Response:
    team = Team.objects.filter(id=team_id).first()
    if not team:
        return Response({"error": "Team not found"}, status=404)

    serialized_team = TeamSerializer(team)
    return Response(serialized_team.data, status=200)


class TeamsView(generics.ListAPIView):
    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Team.objects.order_by("normalized_name").all()
        name = self.request.query_params.get("name", None)
        if name is not None:
            queryset = queryset.filter(name__icontains=name)
        return queryset
