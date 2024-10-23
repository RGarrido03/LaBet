from datetime import datetime
from typing import Any

import requests
import json

from django.conf import settings
from unidecode import unidecode

from app.models import *


class BetclicScrapper:
    """docstring for BetclicScrapper."""

    def __init__(
        self,
        url="https://offer.cdn.begmedia.com/api/pub/v4/sports/1?application=1024&countrycode=en&hasSwitchMtc=true&language=pt&limit=500&markettypeId=1365&offset=0&sitecode=ptpt&sortBy=ByLiveRankingPreliveDate",
    ):
        self.url = url
        self.data = None
        self.parsed_data = {}
        db_obj = BetHouse.objects.filter(name="Betclic").first()
        self.bet_house = (
            BetHouse.objects.create(name="Betclic", logo="", website="betclic.pt")
            if not db_obj
            else db_obj
        )

    def scrap(self):
        response = requests.get(self.url)
        self.data = json.loads(response.text)
        self.parsed_data = self.parse_json()
        return self.parsed_data

    def parse_event(self, event: dict[str, Any]) -> GameOdd | None:
        if not event["grouped_markets"]:
            return None

        print(unidecode(event["contestants"][0]["name"]).lower())

        team_1 = Team.objects.filter(
            name__icontains=unidecode(event["contestants"][0]["name"]).lower()
        ).first()
        team_2 = Team.objects.filter(
            name__icontains=unidecode(event["contestants"][1]["name"]).lower()
        ).first()

        if not team_1 or not team_2:
            return None

        date = datetime.fromisoformat(event["date"])

        game = Game.objects.filter(
            home_team=team_1, away_team=team_2, date=date
        ).first()
        game = (
            Game.objects.create(home_team=team_1, away_team=team_2, date=date)
            if not game
            else game
        )

        # TODO: Rever ordem das odds (spoiler: will never be done)
        print(event)
        tmp_var = event["grouped_markets"][0]["markets"][0]["selections"]
        return GameOdd(
            game=game,
            bet_house=self.bet_house,
            home_odd=tmp_var[0][0]["odds"],
            draw_odd=tmp_var[1][0]["odds"],
            away_odd=tmp_var[2][0]["odds"],
        )

    def parse_json(self):
        matches = self.data["matches"]
        clean_data = []
        # i need to clean the data
        for event in matches:
            match = self.parse_event(event)
            if match is None:
                continue
            print(match.__dict__)
            clean_data.append(match)

        return clean_data
