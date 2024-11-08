import logging

from app.modules import lebull, betano, betclic, placard

# Configure o logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler("scraping_debug.log")
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


# Função de scraping com logs detalhados
def perform_scraping():
    scrappers = [
        lebull.LebullScrapper(),
        betano.BetanoScrapper(),
        betclic.BetclicScrapper(),
        placard.PlacardScrapper(),
    ]

    for scrapper in scrappers:
        logger.info(f"Starting scraping for {scrapper.name}")

        try:
            game_odds = scrapper.scrap()
            logger.info(f"Scraped {len(game_odds)} odds from {scrapper.name}")
        except Exception as e:
            # Captura erros gerais e os registra
            logger.error(f"Error scraping {scrapper.name}: {e}", exc_info=True)

    logger.info("Completed all scraping tasks")


def send_email(recipient, subject, message):
    # Placeholder for email sending logic
    print(f"Sending email to {recipient}")
