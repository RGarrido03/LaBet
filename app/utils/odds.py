import random
from typing import Any

from app.models import GameOdd
from app.serializers import BetHouseSerializer


def normalize_odds(hodd: float, dodd: float, aodd: float) -> tuple[float, float, float]:
    return randomize_odd(hodd), randomize_odd(dodd), randomize_odd(aodd)


def randomize_odd(odd: float) -> float:
    return odd + random.gauss(0, 0.2)


def calculate_arbitrage(home: float, draw: float, away: float) -> float:
    return 1 / home + 1 / draw + 1 / away


def get_best_combination(odds: list[GameOdd]) -> dict[str, Any] | None:
    if len(odds) == 1:
        return None

    home = max(odds, key=lambda x: x.home_odd)
    draw = max(odds, key=lambda x: x.draw_odd)
    away = max(odds, key=lambda x: x.away_odd)
    odd = float(
        1 / home.home_odd + (1 / draw.draw_odd if draw else 0) + 1 / away.away_odd
    )

    return {
        "home": {
            "house": BetHouseSerializer(home.bet_house).data,
            "odd": home.home_odd,
        },
        "draw": (
            {
                "house": BetHouseSerializer(draw.bet_house).data,
                "odd": draw.draw_odd,
            }
            if draw
            else None
        ),
        "away": {
            "house": BetHouseSerializer(away.bet_house).data,
            "odd": away.away_odd,
        },
        "odd": odd,
    }
