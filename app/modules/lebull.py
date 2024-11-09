from datetime import datetime, timedelta

from app.modules.scrapper import Scrapper


class LebullScrapper(Scrapper):
    def __init__(self):
        def aux_extractor(x):  # x[date]
            epoch, delta = x.replace("/Date(", "").replace(")/", "").split("+")
            epoch = int(epoch) / 1000

            return str(datetime.fromtimestamp(epoch) + timedelta(hours=int(delta) / 100))

        super().__init__(
            "Lebull",
            "https://www.lebull.pt",
            "https://feelinglucky.pt/wp-content/uploads/2024/09/lebull-logo.svg",
            lambda x: x["stakeTypes"][0]["stakes"][0]["stakeName"],
            lambda x: x["stakeTypes"][0]["stakes"][2]["stakeName"],
            lambda x: aux_extractor(x["date"]),
            lambda x: x["stakeTypes"][0]["stakes"][0]["betFactor"],
            lambda x: x["stakeTypes"][0]["stakes"][1]["betFactor"],
            lambda x: x["stakeTypes"][0]["stakes"][2]["betFactor"],
        )

    def scrap(self):
        # FIXME RUBEN this needs refactor and i can't

        import requests

        headers = {
            "accept": "*/*",
            "accept-language": "pt-PT,pt;q=0.9,en-GB;q=0.8,en;q=0.7,pt-BR;q=0.6,en-US;q=0.5,es;q=0.4",
            "cache-control": "no-cache",
            "origin": "https://lebull-sportsbook-prod.gtdevteam.work",
            "pragma": "no-cache",
            "priority": "u=1, i",
            "referer": "https://lebull-sportsbook-prod.gtdevteam.work/",
            "sec-ch-ua": '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Linux"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
            "x-auth-tenant-id": "126dc7bf-288b-4f72-9536-3aa54648c0f4",
        }

        params = {
            "languageId": "14",
            "timeFilter": "0",
        }
        url = "https://sportsbook-betting-prod.gtdevteam.work/sports"

        response = requests.request("GET", url, headers=headers, params=params)
        data = response.json()
        print(response.json())
        league_ids = {}  # sport id : [league ids]
        for d in data["sports"]:
            sport_id = d["sportId"]
            for country in d["countries"]:
                for league in country["leagues"]:
                    league_id = league["leagueId"]
                    league_name = league["leagueName"]
                    if sport_id not in league_ids:
                        league_ids[sport_id] = []
                    league_ids[sport_id].append((league_id, league_name))

        # pp.pprint(league_ids[1])
        # agora precisamos de dar get de todos os jogos de cada liga

        params = {
            "leagueTimeFilter": "10",
            "languageId": "14",
            "stakeTypes": "[1]",
            "isStakeGrouped": "true",
            "timeZone": "0",
            "checkIsActive": "true",
            "setParameterOrder": "false",
            "getMainMatch": "false",
        }

        matches = []
        for l_id, l_name in league_ids[1]:

            response = requests.get(
                "https://sportsbook-betting-prod.gtdevteam.work/leagues/"
                + str(l_id)
                + "/upcoming",
                params=params,
                headers=headers,
            )

            g = response.json()
            # check if there is any game
            if len(g) == 0:
                continue

            games = g[0]["games"]
            # parse events
            for game in games:

                event = self.parse_event(game) if len(game["stakeTypes"][0]["stakes"]) == 3 else None
                if event:
                    print(event)
                    matches.append(event)

        return matches
