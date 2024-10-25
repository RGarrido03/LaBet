from datetime import datetime
from typing import Any

from app.models import Game, GameOdd
from app.modules.scrapper import Scrapper


class BetclicScrapper(Scrapper):
    def __init__(
        self,
    ):
        super().__init__(
            "Betclic",
            "https://www.betclic.pt",
            "https://upload.wikimedia.org/wikipedia/commons/f/fe/Logo_Betclic_2019.svg",
        )
        self.limit = 50
        self.bet_house = self.get_or_create_bet_house()
        self.url = f"https://offer.cdn.begmedia.com/api/pub/v4/sports/1?application=1024&countrycode=en&hasSwitchMtc=true&language=pt&limit={self.limit}&markettypeId=1365&offset=0&sitecode=ptpt&sortBy=ByLiveRankingPreliveDate"

    def scrap(self) -> list[GameOdd]:
        """Fetch data from API and parse the response."""
        self.data = self.make_request("GET", self.url)
        return self.parse_json()

    def parse_event(self, event: dict[str, Any]) -> GameOdd | None:
        """Parse a single event and return a GameOdd object if valid."""
        if len(event.get("grouped_markets")) < 1:
            self.logger.info("Skipping event, no grouped markets.")
            return None

        team_1 = self.get_team(event["contestants"][0]["name"])
        team_2 = self.get_team(event["contestants"][1]["name"])

        if not team_1 or not team_2:
            self.logger.info("Skipping event, one or both teams not found.")
            self.logger.info(f"Team 1: {team_1}, Team 2: {team_2}")
            self.logger.info(f"Event: {event}")
            return None

        date = datetime.fromisoformat(event["date"])

        (game, _) = Game.objects.get_or_create(
            home_team=team_1, away_team=team_2, date=date
        )

        try:
            odds = event["grouped_markets"][0]["markets"][0]["selections"]

            # FOR OTHER SPORTS THIS NEEDS TO BE REFACTORED
            return GameOdd(
                game=game,
                bet_house=self.bet_house,
                home_odd=odds[0][0]["odds"],
                draw_odd=odds[1][0]["odds"],
                away_odd=odds[2][0]["odds"],
            )
        except (KeyError, IndexError) as e:
            self.logger.error(f"Error parsing odds for event: {event}, error: {e}")
            return None

    def parse_json(self) -> list[GameOdd]:
        """Parse the fetched JSON data and return the cleaned list of GameOdd."""
        if not self.data or "matches" not in self.data:
            self.logger.error("Invalid or empty data.")
            return []

        return [
            match
            for event in self.data["matches"]
            if (match := self.parse_event(event))
        ]
