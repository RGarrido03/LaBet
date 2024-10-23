from datetime import datetime
from typing import Any, Optional

import requests
import json
import logging

from django.conf import settings
from unidecode import unidecode

from app.models import BetHouse, Game, Team, GameOdd



class BetclicScrapper:
    def __init__(
        self,
        url: str = "https://offer.cdn.begmedia.com/api/pub/v4/sports/1?application=1024&countrycode=en&hasSwitchMtc=true&language=pt&limit=500&markettypeId=1365&offset=0&sitecode=ptpt&sortBy=ByLiveRankingPreliveDate",
    ):
        self.url = url
        self.data: Optional[dict] = None
        self.parsed_data: list[GameOdd] = []
        self.bet_house = self.get_or_create_bet_house()
        self.logger =logging.getLogger(__name__)
        # add a file handler
         self.logger.addHandler(logging.FileHandler(settings.LOG_FILE))

    def get_or_create_bet_house(self) -> BetHouse:
        """Retrieve or create the Betclic BetHouse object."""
        db_obj = BetHouse.objects.filter(name="Betclic").first()
        if not db_obj:
            return BetHouse.objects.create(name="Betclic", logo="", website="betclic.pt")
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

    def parse_event(self, event: dict[str, Any]) -> Optional[GameOdd]:
        """Parse a single event and return a GameOdd object if valid."""
        if not event.get("grouped_markets"):
            self.logger.info("Skipping event, no grouped markets.")
            return None

        team_1 = self.get_team_from_event(event, 0)
        team_2 = self.get_team_from_event(event, 1)

        if not team_1 or not team_2:
            self.logger.info("Skipping event, one or both teams not found.")
            return None

        date = datetime.fromisoformat(event["date"])

        game = Game.objects.filter(home_team=team_1, away_team=team_2, date=date).first()
        if not game:
            game = Game.objects.create(home_team=team_1, away_team=team_2, date=date)

        try:
            odds = event["grouped_markets"][0]["markets"][0]["selections"]
            return GameOdd(
                game=game,
                bet_house=self.bet_house,
                home_odd=odds[0]["odds"],
                draw_odd=odds[1]["odds"],
                away_odd=odds[2]["odds"],
            )
        except (KeyError, IndexError) as e:
            self.logger.error(f"Error parsing odds for event: {event}, error: {e}")
            return None

    def get_team_from_event(self, event: dict, index: int) -> Optional[Team]:
        """Helper function to extract team object based on the event data."""
        try:
            team_name = unidecode(event["contestants"][index]["name"]).lower()
            return Team.objects.filter(name__icontains=team_name).first()
        except (IndexError, KeyError) as e:
            self.logger.error(f"Error extracting team from event: {event}, error: {e}")
            return None

    def parse_json(self) -> list[GameOdd]:
        """Parse the fetched JSON data and return the cleaned list of GameOdd."""
        if not self.data or "matches" not in self.data:
            self.logger.error("Invalid or empty data.")
            return []

        clean_data = []
        for event in self.data["matches"]:
            match = self.parse_event(event)
            if match:
                clean_data.append(match)

        return clean_data
