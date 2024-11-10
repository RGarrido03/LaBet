import logging
from abc import ABC, abstractmethod
from datetime import datetime
from json import JSONDecodeError
from typing import Optional, Any, Callable

import requests
from django.conf import settings
from requests import RequestException
from unidecode import unidecode

from app.models import GameOdd, Team, BetHouse, Game
from app.utils.odds import normalize_odds
from app.utils.similarity import get_most_similar_name


# abstract class for scrapper
class Scrapper(ABC):
    def __init__(
            self,
            name: str,
            website: str,
            logo: str,
            hteam_extractor: Callable,
            ateam_extractor: Callable,
            date_extractor: Callable = None,
            hodd_extractor: Callable = None,
            dodd_extractor: Callable = None,
            aodd_extractor: Callable = None,
    ):
        self.name: str = name
        self.website: str = website
        self.logo: str = logo
        self.bet_house = self.get_or_create_bet_house()

        self.hteam_extractor = hteam_extractor
        self.ateam_extractor = ateam_extractor
        self.date_extractor = date_extractor
        self.hodd_extractor = hodd_extractor
        self.dodd_extractor = dodd_extractor
        self.aodd_extractor = aodd_extractor

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(logging.FileHandler(settings.LOG_FILE))
        self.logger.addHandler(logging.StreamHandler())

        self.data: Optional[dict] = None
        self.parsed_data: list[GameOdd] = []

    def get_or_create_bet_house(self):
        db_obj = BetHouse.objects.filter(name=self.name).first()
        if not db_obj:
            return BetHouse.objects.create(
                name=self.name,
                logo=self.logo,
                website=self.website,
            )
        return db_obj

    def get_team(self, name: str) -> Team | None:
        try:
            team_name = unidecode(name).lower()
            team = Team.objects.filter(normalized_name__icontains=team_name).first()

            if team:
                return team

            all_teams = Team.objects.values_list("normalized_name", flat=True)
            most_similar_team = get_most_similar_name(team_name, all_teams)[0]

            if most_similar_team:
                team = Team.objects.filter(
                    normalized_name__icontains=most_similar_team
                ).first()
                self.logger.info(
                    "Team %s not found; using %s.", team_name, most_similar_team
                )
                return team

            self.logger.warning(f"Could not find team similar to {team_name}")
            return None

        except (Team.DoesNotExist, IndexError, KeyError) as e:
            self.logger.warning("Could not find team: %s", e)
            return None

    def make_request(
            self, method: str, url: str, headers: dict[str, Any] = None, data: Any = None
    ) -> dict[str, Any]:
        try:
            proxies = {
                'https': 'http://20.111.54.16:8123'
            }
            response = requests.request(method, url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            self.logger.error(f"Error fetching data: {e}")
        except JSONDecodeError as e:
            self.logger.error(f"Error decoding JSON: {e}")

    def parse_event(self, event: dict[str, Any]) -> GameOdd | None:
        """Parse a single event and return a GameOdd object if valid."""
        team_1 = self.get_team(self.hteam_extractor(event))
        team_2 = self.get_team(self.ateam_extractor(event))

        if not team_1 or not team_2:
            self.logger.info("Skipping event, one or both teams not found.")
            self.logger.info(f"Team 1: {team_1}, Team 2: {team_2}")
            self.logger.info(f"Event: {event}")
            return None

        date = datetime.fromisoformat(self.date_extractor(event))

        (game, _) = Game.objects.get_or_create(
            home_team=team_1, away_team=team_2, date=date
        )

        home_odd = float(self.hodd_extractor(event))
        draw_odd = float(self.dodd_extractor(event))
        away_odd = float(self.aodd_extractor(event))

        (home_odd, draw_odd, away_odd) = normalize_odds(home_odd, draw_odd, away_odd)

        try:
            # check if the game already exists but the odds will always be diferent
            # because of the normalization
            game_odd = GameOdd.objects.filter(game=game, bet_house=self.bet_house).first()
            if game_odd:
                return game_odd

            (game_odd, created) = GameOdd.objects.get_or_create(
                game=game,
                bet_house=self.bet_house,
                home_odd=home_odd,
                draw_odd=draw_odd,
                away_odd=away_odd,
            )
            return game_odd if created else None
        except (KeyError, IndexError) as e:
            self.logger.error(f"Error parsing odds for event: {event}, error: {e}")
            return None

    @abstractmethod
    def scrap(self) -> list[GameOdd]:
        pass
