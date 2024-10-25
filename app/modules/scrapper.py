import logging
from abc import ABC, abstractmethod
from typing import Optional, Any

from django.conf import settings

from app.models import GameOdd, Team, BetHouse


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
    def get_team_from_event(self, event: dict, index: int) -> Optional[Team]:
        pass
