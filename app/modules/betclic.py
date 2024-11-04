from typing import Any, override

from app.models import GameOdd
from app.modules.scrapper import Scrapper


class BetclicScrapper(Scrapper):
    def __init__(self):
        team_extractor = lambda x, idx: x["contestants"][idx]["name"]
        odds_extractor = lambda x, idx: x["grouped_markets"][0]["markets"][0][
            "selections"
        ][idx][0]["odds"]
        super().__init__(
            "Betclic",
            "https://www.betclic.pt",
            "https://upload.wikimedia.org/wikipedia/commons/f/fe/Logo_Betclic_2019.svg",
            lambda x: team_extractor(x, 0),
            lambda x: team_extractor(x, 1),
            lambda x: x["date"],
            lambda x: odds_extractor(x, 0),
            lambda x: odds_extractor(x, 1),
            lambda x: odds_extractor(x, 2),
        )
        self.limit = 50
        self.bet_house = self.get_or_create_bet_house()
        self.url = f"https://offer.cdn.begmedia.com/api/pub/v4/sports/1?application=1024&countrycode=en&hasSwitchMtc=true&language=pt&limit={self.limit}&markettypeId=1365&offset=0&sitecode=ptpt&sortBy=ByLiveRankingPreliveDate"

    def scrap(self) -> list[GameOdd]:
        """Fetch data from API and parse the response."""
        data = self.make_request("GET", self.url)

        if not data or "matches" not in data:
            self.logger.error("Invalid or empty data.")
            return []

        return [
            match for event in data["matches"] if (match := self.parse_event(event))
        ]

    @override
    def parse_event(self, event: dict[str, Any]) -> GameOdd | None:
        """Parse a single event and return a GameOdd object if valid."""
        if len(event.get("grouped_markets")) < 1:
            self.logger.info("Skipping event, no grouped markets.")
            return None

        return super().parse_event(event)
