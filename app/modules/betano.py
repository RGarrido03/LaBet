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
            import http.client
            import gzip
            import io

            # Configurando a conexão e os headers
            conn = http.client.HTTPSConnection("www.betano.pt")
            headers = {
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

            # Fazendo a requisição GET
            conn.request("GET", "/api/sport/futebol/jogos-de-hoje/", headers=headers)
            response = conn.getresponse()

            # Lendo os dados da resposta
            compressed_data = response.read()

            # Verificando se a resposta está compactada em gzip
            if response.getheader("Content-Encoding") == "gzip":
                # Descomprimindo os dados gzip
                with gzip.GzipFile(
                    fileobj=io.BytesIO(compressed_data)
                ) as decompressed_file:
                    decompressed_data = decompressed_file.read()
            else:
                decompressed_data = compressed_data

            # Decodificando os dados
            decoded_data = decompressed_data.decode("utf-8")

            # Exibindo o conteúdo
            print(decoded_data)

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
