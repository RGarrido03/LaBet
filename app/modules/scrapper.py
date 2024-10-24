import logging
from datetime import datetime
from typing import Optional, Any
from django.conf import settings
from app.models import BetHouse, Game, GameOdd, Team
from abc import ABC, abstractmethod


# abstract class for scrapper
class Scrapper(ABC):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(logging.FileHandler(settings.LOG_FILE))
        self.logger.addHandler(logging.StreamHandler())
        self.data: Optional[dict] = None
        self.parsed_data: list[GameOdd] = []
        self.bet_house = self.get_or_create_bet_house()
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

    @abstractmethod
    def get_or_create_bet_house(self):
        pass
