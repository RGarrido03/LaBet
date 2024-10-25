import logging
from abc import ABC, abstractmethod
from json import JSONDecodeError
from typing import Optional, Any

import requests
from django.conf import settings
from requests import RequestException
from unidecode import unidecode

from app.models import GameOdd, Team, BetHouse
from app.utils.similarity import get_most_similar_name


# abstract class for scrapper
class Scrapper(ABC):
    def __init__(self, name: str, website: str, logo: str):
        self.name: str = name
        self.website: str = website
        self.logo: str = logo
        self.bet_house = self.get_or_create_bet_house()

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
            team = Team.objects.filter(name__icontains=team_name).first()

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
            response = requests.request(method, url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            self.logger.error(f"Error fetching data: {e}")
        except JSONDecodeError as e:
            self.logger.error(f"Error decoding JSON: {e}")

    @abstractmethod
    def scrap(self) -> list[GameOdd]:
        pass

    @abstractmethod
    def parse_json(self):
        pass

    @abstractmethod
    def parse_event(self, event: dict[str, Any]) -> Optional[GameOdd]:
        pass

    @abstractmethod
    def get_team_from_event(self, event: dict, index: int) -> Team | None:
        pass
