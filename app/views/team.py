from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from app.models import Game, Team
from app.serializers import GameSerializer


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
