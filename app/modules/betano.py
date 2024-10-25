import json
from typing import Any, Optional
import requests
from app.models import *
from app.modules.scrapper import Scrapper


class BetanoScrapper(Scrapper):
    def __init__(self):
        super().__init__(
            ...,
            ...,
            ...,
            ...,
            ...,
            ...,
            ...,
            ...,
        )
        self.bet_house = self.get_or_create_bet_house()
        self.url = "https://www.betano.pt/api/sport/futebol/jogos-de-hoje/"

    def get_or_create_bet_house(self) -> BetHouse:
        """Retrieve or create the Betano BetHouse object."""
        db_obj = BetHouse.objects.filter(name="Betano").first()
        if not db_obj:
            return BetHouse.objects.create(name="Betano", logo="", website="betano.pt")
        return db_obj

    def scrap(self) -> list[GameOdd]:
        """Fetch data from API and parse the response."""
        try:
            import httpx

            payload = ""
            headers = {
                "cookie": "__cf_bm=G_mlLk8j3pPnNx0IDdMbs7lm.hbXKtEl.TDX8Cgwvq0-1729820377-1.0.1.1-glua9.Xipq6jUK5tSyDjV2aBPlpm8dCkMxhTcK7cCO2LRlanVnKGep9wFH26BHHNHFLz.B7ME3EOIW.E.aeWOw; _cfuvid=2H8KjhydB93fF7qx.qvANaahXRI2i9v.GxoDo3ZLmx4-1729817862539-0.0.1.1-604800000",
                "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:131.0) Gecko/20100101 Firefox/131.0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
                "Accept-Language": "pt-PT,pt;q=0.8,en;q=0.5,en-US;q=0.3",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Connection": "keep-alive",
                "Cookie": "_cfuvid=r5ANt7VbzbumhmUNmoUzvVEWfM3wUVBV0sVHgDtLpzI-1729817804655-0.0.1.1-604800000; __cf_bm=xITR4NX5VlwhPYDf.QirP8E.v8km972ablqb0VkjdmA-1729820568-1.0.1.1-xzJGYwZ5mynbYiuTvaVYZYnZY2uVYvfyX0suDKqt2oTNtSCz18UUJWeiQ8LXLnpQWUK2iIEu27JjtJRk1UgYAg",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "cross-site",
                "Priority": "u=0, i",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
            }

            with httpx.Client(http2=True) as client:
                response = client.get(self.url, headers=headers)
                # Debugando o status e o conteúdo da resposta
                print("Status code:", response.status_code)
                print("Headers recebidos:", response.headers)
                print("Texto da resposta:", response.text)

            # Verifique se a resposta foi bem-sucedida
            response = requests.request(
                "GET",
                self.url,
                data=payload,
                headers=headers,
            )

            print(response.text)
            response.raise_for_status()  # Ensure HTTP errors are handled
            self.data = response.json()  # Load the response as JSON
            print(self.data)
            # self.parsed_data = self.parse_json()
        except requests.RequestException as e:
            self.logger.error(f"Error fetching data: {e}")
        except json.JSONDecodeError as e:
            self.logger.error(f"Error decoding JSON: {e}")

        return self.parsed_data

    def parse_event(self, event: dict[str, Any]) -> Optional[GameOdd]:
        """Parse a single event and return a GameOdd object if valid."""
        # Parse the event
        return None

    def get_team_from_event(self, event: dict[str, Any], index: int) -> Optional[Team]:
        """Extract and return a Team object from the event data."""
        # Extract team data
        return None

    def parse_json(self) -> list[GameOdd]:
        """Parse the fetched JSON data and return the cleaned list of GameOdd."""
        # Parse the JSON data
        return []
