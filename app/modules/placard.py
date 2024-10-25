import datetime
from typing import Optional, Any, List

from app.models import *
from app.modules.scrapper import Scrapper


class PlacardScrapper(Scrapper):
    def __init__(self):
        super().__init__(
            "Placard",
            "https://www.placard.pt",
            "https://www.placard.pt/library/logo/Placard_pt.svg",
        )
        self.competitions_url = "https://placard.jogossantacasa.pt/PlacardWeb/screenservices/Plcard_WebEvents_CW/EventsFlow/EventList_MB/DataActionGetRegionCompetitionData"
        self.url = "https://placard.jogossantacasa.pt/PlacardWeb/screenservices/Plcard_WebEvents_CW/EventsFlow/EventList_EventListBlock/DataActionGetEventsData"
        self.today = str(datetime.date.today())

    def scrap(self):
        competition_ids = self._get_all_competitions_ids()
        matches = []

        for competition_id in competition_ids:
            competition_data = self._get_competition_data(competition_id)
            event_data_list = competition_data["data"]["EventDataList"]["List"]

            for event in event_data_list:
                match = self.parse_event(event)
                if match:
                    matches.append(match)

        self.logger.info("Scraping completed. Total matches found: %d", len(matches))
        return matches

    def parse_event(self, event: dict[str, Any]) -> Optional[GameOdd]:
        try:
            event_date = event["StartDateTime"]
            home_team = self.get_team(event["HomeOpponent"])
            away_team = self.get_team(event["AwayOpponent"])
            if not home_team or not away_team:
                self.logger.warning(
                    f"Missing team data for event, teams home { home_team } and away { away_team },\n supose home { event["HomeOpponent"] } and supose away { event['AwayOpponent'] }",
                )
                return None

            home_odd = float(event["MarketOutcome1_Price"])
            away_odd = float(event["MarketOutcome3_Price"])
            draw_odd = float(event["MarketOutcome2_Price"])

            (game, _) = Game.objects.get_or_create(
                home_team=home_team, away_team=away_team, date=event_date
            )

            self.logger.info(
                "Parsed odds for game %s vs %s: Home: %f, Away: %f, Draw: %f",
                home_team,
                away_team,
                home_odd,
                away_odd,
                draw_odd,
            )

            return GameOdd(
                game=game,
                bet_house=self.bet_house,
                home_odd=home_odd,
                away_odd=away_odd,
                draw_odd=draw_odd,
            )

        except (KeyError, ValueError) as e:
            print(f"Error while parsing event: {e}")
            return None

    def _get_all_competitions_ids(self) -> List[Any]:
        headers = {
            "Accept": "application/json",
            "Accept-Language": "pt-PT,pt;q=0.9,en-GB;q=0.8,en;q=0.7,pt-BR;q=0.6,en-US;q=0.5,es;q=0.4",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "application/json; charset=UTF-8",
            "Cookie": "AVIJS073266D0572A0D13=/PlacardWeb; osVisitor=c794c152-a072-447b-83e4-1211bda9a00d; nr1Users=lid%3dAnonymous%3btuu%3d0%3bexp%3d0%3brhs%3dXBC1ss1nOgYW1SmqUjSxLucVOAg%3d%3bhmc%3dpOq%2bkIo%2bDYIzKoOhG33hGSk1kfw%3d; nr2Users=crf%3dT6C%2b9iB49TLra4jEsMeSckDMNhQ%3d%3buid%3d0%3bunm%3d; NavSessionId=d497e5b1-f5a2-4cca-beed-6745396ca85f; osVisit=55435153-0b5f-45cd-b199-72cc8f5a5383",
            "Origin": "https://placard.jogossantacasa.pt",
            "Pragma": "no-cache",
            "Referer": "https://placard.jogossantacasa.pt/PlacardWeb/Events",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            "X-CSRFToken": "T6C+9iB49TLra4jEsMeSckDMNhQ=",
            "sec-ch-ua": '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Linux"',
        }

        data = {
            "versionInfo": {
                "moduleVersion": "NRDbYlvDXVMg02KtTge10g",
                "apiVersion": "tXWBZZVwVY5UKMLWuZd3yQ",
            },
            "viewName": "Events.Events",
            "screenData": {
                "variables": {
                    "SelectedCompetitionsList": {
                        "List": [],
                        "EmptyListItem": {
                            "CompetionId": "",
                            "CompetitionName": "",
                            "RegionName": "",
                        },
                    },
                    "Previous_CompetitionId": "",
                    "Previous_RegionName": "",
                    "Previous_CompetionName": "",
                    "SelectedModalityId": "football",
                    "_selectedModalityIdInDataFetchStatus": 1,
                    "RegionName": "",
                    "_regionNameInDataFetchStatus": 1,
                    "SelectedCompetitionId": "",
                    "_selectedCompetitionIdInDataFetchStatus": 1,
                    "CompetionName": "",
                    "_competionNameInDataFetchStatus": 1,
                    "Initial_SelectedDate": "1900-01-01",
                    "_initial_SelectedDateInDataFetchStatus": 1,
                    "GetEventCalendarNavigation": {
                        "NavigationList": {
                            "List": [
                                {
                                    "Date": self.today,
                                    "HasOpenBets": True,
                                    "EventNavigationId": "CurrDate",
                                }
                            ]
                        },
                        "SelectedDate": self.today,
                        "SelectedNavigationId": "CurrDate",
                        "DataFetchStatus": 1,
                    },
                }
            },
        }

        response = self.make_request(
            "POST", self.competitions_url, headers=headers, data=data
        )

        competition_ids = [
            competition["CompetitionId"]
            for competition_data in response["data"]["CompetitionDataList"]["List"]
            for competition in competition_data["CompetitionList"]["List"]
        ]
        self.logger.info("Found %d competitions.", len(competition_ids))

        return competition_ids

    def _get_competition_data(self, competition_id: str) -> dict:
        headers = {
            "Accept": "application/json",
            "Accept-Language": "pt-PT,pt;q=0.9,en-GB;q=0.8,en;q=0.7,pt-BR;q=0.6,en-US;q=0.5,es;q=0.4",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "application/json; charset=UTF-8",
            "Cookie": "AVIJS073266D0537D0BF7=/PlacardWeb; osVisitor=c794c152-a072-447b-83e4-1211bda9a00d; nr1Users=lid%3dAnonymous%3btuu%3d0%3bexp%3d0%3brhs%3dXBC1ss1nOgYW1SmqUjSxLucVOAg%3d%3bhmc%3dpOq%2bkIo%2bDYIzKoOhG33hGSk1kfw%3d; nr2Users=crf%3dT6C%2b9iB49TLra4jEsMeSckDMNhQ%3d%3buid%3d0%3bunm%3d; NavSessionId=d497e5b1-f5a2-4cca-beed-6745396ca85f; osVisit=55435153-0b5f-45cd-b199-72cc8f5a5383",
            "Origin": "https://placard.jogossantacasa.pt",
            "Pragma": "no-cache",
            "Referer": "https://placard.jogossantacasa.pt/PlacardWeb/Events",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            "X-CSRFToken": "T6C+9iB49TLra4jEsMeSckDMNhQ=",
            "sec-ch-ua": '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Linux"',
        }

        data = {
            "versionInfo": {
                "moduleVersion": "NRDbYlvDXVMg02KtTge10g",
                "apiVersion": "19zlE5vtzBB1w20h7QXb6A",
            },
            "viewName": "Events.Events",
            "screenData": {
                "variables": {
                    "SelectedCompetitionId": competition_id,  # change here
                    "_selectedCompetitionIdInDataFetchStatus": 1,
                    "SelectedDate": self.today,  # change here to today
                    "_selectedDateInDataFetchStatus": 1,
                    "SelectedModalityId": "football",
                    "_selectedModalityIdInDataFetchStatus": 1,
                    "SelectedNavigationId": "CurrDate",
                    "_selectedNavigationIdInDataFetchStatus": 1,
                }
            },
        }

        return self.make_request("POST", self.url, headers=headers, data=data)
