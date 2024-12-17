import json
import re
from typing import Any

import requests

from app.models import GameOdd
from app.modules.scrapper import Scrapper


class BetclicScrapper(Scrapper):
    def __init__(self):
        team_extractor = lambda x, idx: x["contestants"][idx]["name"]
        odds_extractor = lambda x, idx: x["market"]["mainSelections"][idx]["odds"]
        super().__init__(
            "Betclic",
            "https://www.betclic.pt",
            "https://upload.wikimedia.org/wikipedia/commons/f/fe/Logo_Betclic_2019.svg",
            lambda x: team_extractor(x, 0),
            lambda x: team_extractor(x, 1),
            lambda x: x["matchDateUtc"],
            lambda x: odds_extractor(x, 0),
            lambda x: odds_extractor(x, 1),
            lambda x: odds_extractor(x, 2),
        )

        self.limit = 500
        self.bet_house = self.get_or_create_bet_house()
        self.url = f"https://www.betclic.pt/futebol-sfootball"

    def scrap(self) -> list[GameOdd]:
        """Fetch data from API and parse the response."""
        data = requests.get(self.url).text
        match = re.search(
            r'<script id="ng-state" type="application/json">\s*(.*?)\s*</script>',
            data,
            re.DOTALL,
        )

        if not match:
            self.logger.error("Invalid data.")
            return []

        dct: dict[str, Any] = json.loads(match.group(1))

        if not dct:
            self.logger.error("Invalid data.")
            return []

        idx = None
        for k, v in dct.items():
            if not isinstance(v, dict) or "response" not in v:
                continue
            if "payload" not in v["response"]:
                continue
            if "matches" in v["response"]["payload"]:
                idx = k
                break

        if not idx:
            self.logger.error("Invalid data.")
            return []

        return [
            match
            for event in dct[idx]["response"]["payload"]["matches"]
            if (match := self.parse_event(event))
        ]
