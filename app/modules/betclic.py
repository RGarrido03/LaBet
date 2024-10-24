import json
from datetime import datetime
from typing import Any

import requests
from unidecode import unidecode

from app.models import BetHouse, Game, Team, GameOdd
from app.modules.scrapper import Scrapper
from app.utils.similarity import get_most_similar_name


class BetclicScrapper(Scrapper):
    def __init__(
        self,
    ):
        super().__init__()
        self.limit = 50
        self.bet_house = self.get_or_create_bet_house()
        self.url = f"https://offer.cdn.begmedia.com/api/pub/v4/sports/1?application=1024&countrycode=en&hasSwitchMtc=true&language=pt&limit={self.limit}&markettypeId=1365&offset=0&sitecode=ptpt&sortBy=ByLiveRankingPreliveDate"

    def get_or_create_bet_house(self) -> BetHouse:
        """Retrieve or create the Betclic BetHouse object."""
        db_obj = BetHouse.objects.filter(name="Betclic").first()
        if not db_obj:
            return BetHouse.objects.create(
                name="Betclic",
                logo="https://upload.wikimedia.org/wikipedia/commons/f/fe/Logo_Betclic_2019.svg",
                website="betclic.pt",
            )
        return db_obj

    def scrap(self) -> list[GameOdd]:
        """Fetch data from API and parse the response."""
        try:
            response = requests.get(self.url)
            response.raise_for_status()  # Ensure HTTP errors are handled
            self.data = response.json()  # Load the response as JSON
            self.parsed_data = self.parse_json()
        except requests.RequestException as e:
            self.logger.error(f"Error fetching data: {e}")
        except json.JSONDecodeError as e:
            self.logger.error(f"Error decoding JSON: {e}")
        return self.parsed_data

    def parse_event(self, event: dict[str, Any]) -> GameOdd | None:
        """Parse a single event and return a GameOdd object if valid."""
        if len(event.get("grouped_markets")) < 1:
            self.logger.info("Skipping event, no grouped markets.")
            return None

        team_1 = self.get_team_from_event(event, 0)
        team_2 = self.get_team_from_event(event, 1)

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

    def get_team_from_event(self, event: dict, index: int) -> Team | None:
        """Helper function to extract team object based on the event data."""
        try:
            teamname = unidecode(event["contestants"][index]["name"]).lower()
            team = Team.objects.filter(normalized_name__icontains=teamname).first()
            if team:
                return team

            all_teams = Team.objects.values_list("normalized_name", flat=True)
            most_similar_team = get_most_similar_name(teamname, all_teams)[0]

            if most_similar_team:
                return Team.objects.filter(
                    normalized_name__icontains=most_similar_team
                ).first()
            return None
        except (IndexError, KeyError) as e:
            self.logger.error(f"Error extracting team from event: {event}, error: {e}")
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
