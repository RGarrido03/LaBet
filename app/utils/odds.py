import itertools

from app.models import GameOdd, BetHouse


def calculate_arbitrage(home: GameOdd, draw: GameOdd | None, away: GameOdd) -> float:
    return float(
        1 / home.home_odd + (1 / draw.draw_odd if draw else 0) + 1 / away.away_odd
    )


def calculate_combinations(
    game_odds: list[GameOdd], has_draw: bool = True
) -> list[dict[str, BetHouse | float]]:
    combinations: list[tuple[GameOdd, ...]] = list(
        itertools.product(game_odds, repeat=3 if has_draw else 2)
    )

    if not has_draw:
        return [
            {
                "home_house": pair[0].bet_house.to_json(),
                "draw_house": None,
                "away_house": pair[1].bet_house.to_json(),
                "odd": odd,
            }
            for pair in combinations
            if (odd := calculate_arbitrage(pair[0], None, pair[1])) < 1
        ]

    return [
        {
            "home_house": pair[0].bet_house.to_json(),
            "draw_house": pair[1].bet_house.to_json(),
            "away_house": pair[2].bet_house.to_json(),
            "odd": odd,
        }
        for pair in combinations
        if (odd := calculate_arbitrage(pair[0], pair[1], pair[2])) < 1
    ]
