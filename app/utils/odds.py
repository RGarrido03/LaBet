import random

from app.models import GameOdd, BetHouse


def normalize_odds(hodd: float, dodd: float, aodd: float) -> tuple[float, float, float]:
    return randomize_odd(hodd), randomize_odd(dodd), randomize_odd(aodd)


def randomize_odd(odd: float) -> float:
    return odd + random.gauss(0, 0.2)


def calculate_arbitrage(home: float, draw: float, away: float) -> float:
    return 1 / home + 1 / draw + 1 / away


def get_best_combination(
    odds: list[GameOdd],
    debug: bool = False,
) -> dict[str, BetHouse | float] | None:
    if len(odds) == 1:
        return None

    if debug:
        print(odds[0].game)
        for odd in odds:
            print(
                "   ",
                odd.bet_house.name,
                (float(odd.home_odd), float(odd.draw_odd), float(odd.away_odd)),
            )

    home = max(odds, key=lambda x: x.home_odd)
    draw = max(odds, key=lambda x: x.draw_odd)
    away = max(odds, key=lambda x: x.away_odd)
    odd = float(
        1 / home.home_odd + (1 / draw.draw_odd if draw else 0) + 1 / away.away_odd
    )

    if debug:
        print(
            "   ",
            "Best odds combination",
            (
                float(home.home_odd),
                float(draw.draw_odd) if draw else None,
                float(away.away_odd),
            ),
            "=>",
            odd,
        )

    return {
        "home": {
            "house": home.bet_house.to_json(),
            "odd": home.home_odd,
        },
        "draw": (
            {
                "house": draw.bet_house.to_json(),
                "odd": draw.draw_odd,
            }
            if draw
            else None
        ),
        "away": {
            "house": away.bet_house.to_json(),
            "odd": away.away_odd,
        },
        "odd": odd,
    }
