import datetime
import gzip
import http.client
import io
import json

from app.models import *
from app.modules.scrapper import Scrapper


class BetanoScrapper(Scrapper):
    def __init__(self):
        super().__init__(
            "Betano",
            "https://www.betano.pt",
            "https://feelinglucky.pt/wp-content/uploads/2024/09/betano-logo.svg",
            lambda event: event["markets"][0]["selections"][0]["fullName"],
            lambda event: event["markets"][0]["selections"][2]["fullName"],
            lambda event: datetime.datetime.fromtimestamp(
                event["startTime"] / 1000
            ).isoformat()
            + "Z",  # vem em epoch
            lambda event: event["markets"][0]["selections"][0]["price"],
            lambda event: event["markets"][0]["selections"][1]["price"],
            lambda event: event["markets"][0]["selections"][2]["price"],
        )
        self.bet_house = self.get_or_create_bet_house()
        self.url = "https://www.betano.pt/api/sport/futebol/jogos-de-hoje/"
        self.base_url = "/api/sport/futebol/jogos-de-hoje/"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:131.0) Gecko/20100101 Firefox/131.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
            "Accept-Language": "pt-PT,pt;q=0.8,en;q=0.5,en-US;q=0.3",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Connection": "keep-alive",
            "Cookie": "__cf_bm=0fWu3pO0Brpp1j8UyBloUXnzc5t0OfRZC3TfZLvcRFc-1729851634-1.0.1.1-FTq1wwyKFMm3.lH2cpR4LEHXMlMAe_PFhlBpBiqzVruD8riKDpCmOiPc3AwcvaeRcZYfKqgUZVaomZVFmHwHAQ; _cfuvid=lCpNIU0wlFZ6F3dIkG2oiLneTedFVc8ZabZV6lk8xmM-1729851634898-0.0.1.1-604800000",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Priority": "u=0, i",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
            "TE": "trailers",
        }
        self.conn = http.client.HTTPSConnection("www.betano.pt")

    def _fetch_page(self, latest_id) -> list:
        """Fetch a page of data from the API and return it as a list of games."""

        params = f"?latestId={latest_id}&req=mb" if latest_id else ""
        self.conn.request("GET", self.base_url + params, headers=self.headers)
        response = self.conn.getresponse()

        compressed_data = response.read()
        if response.getheader("Content-Encoding") == "gzip":
            with gzip.GzipFile(
                fileobj=io.BytesIO(compressed_data)
            ) as decompressed_file:
                decompressed_data = decompressed_file.read()
        else:
            decompressed_data = compressed_data

        decoded_data = decompressed_data.decode("utf-8")
        return json.loads(decoded_data)

    def scrap(self) -> list[GameOdd]:
        """Fetch data from API and parse the response."""
        all_games = []
        latest_id = 0
        now = datetime.datetime.now()

        time_in_24h = now + datetime.timedelta(hours=24)

        timestamp_in_24h = int(time_in_24h.timestamp())
        last_game_time = 0

        while (
            timestamp_in_24h > last_game_time
        ):  # adicionar condicao de paragem , tipo todos os jogos de hoje
            try:
                data = self._fetch_page(latest_id)

                games = data["data"]["blocks"][0]["events"]

                # start time
                # data["data"]["blocks"][0]["events"][x]["startTime"]  # in epoch

                parsed_games = [
                    match
                    for event in games
                    if event["markets"][0]["name"].lower() == "resultado final"
                    and (match := self.parse_event(event))
                ]

                if not parsed_games:
                    break  # Stop if no more games are returned

                all_games.extend(parsed_games)
                latest_id = data["data"]["blocks"][0]["events"][-1]["id"]
                last_game_time = data["data"]["blocks"][0]["events"][-1]["startTime"]
            except Exception as e:
                self.logger.error(f"Betano Error fetching data: {e}")
                break

        # return all_games
        self.parsed_data = all_games

        return self.parsed_data
