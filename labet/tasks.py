import logging

from app.modules import lebull, betano, betclic, placard
from labet import settings

# Configure o logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler(settings.Q_CLUSTER_LOG_FILE)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(logging.StreamHandler())
logger.addHandler(handler)


def perform_scraping_for_lebull():
    scrapper = lebull.LebullScrapper()
    logger.info(f"Starting scraping for {scrapper.name}")

    try:
        game_odds = scrapper.scrap()
        logger.info(f"Scraped {len(game_odds)} odds from {scrapper.name}")
    except Exception as e:
        # Captura erros gerais e os registra
        logger.error(f"Error scraping {scrapper.name}: {e}", exc_info=True)

    logger.info("Completed lebull scraping task")


def perform_scraping_for_betano():
    scrapper = betano.BetanoScrapper()
    logger.info(f"Starting scraping for {scrapper.name}")

    try:
        game_odds = scrapper.scrap()
        logger.info(f"Scraped {len(game_odds)} odds from {scrapper.name}")
    except Exception as e:
        logger.error(f"Error scraping {scrapper.name}: {e}", exc_info=True)

    logger.info("Completed betano scraping task")


def perform_scraping_for_betclic():
    scrapper = betclic.BetclicScrapper()
    logger.info(f"Starting scraping for {scrapper.name}")

    try:
        game_odds = scrapper.scrap()
        logger.info(f"Scraped {len(game_odds)} odds from {scrapper.name}")
    except Exception as e:
        logger.error(f"Error scraping {scrapper.name}: {e}", exc_info=True)

    logger.info("Completed betclic scraping task")


def perform_scraping_for_placard():
    scrapper = placard.PlacardScrapper()
    logger.info(f"Starting scraping for {scrapper.name}")

    try:
        game_odds = scrapper.scrap()
        logger.info(f"Scraped {len(game_odds)} odds from {scrapper.name}")
    except Exception as e:
        logger.error(f"Error scraping {scrapper.name}: {e}", exc_info=True)

    logger.info("Completed placard scrapping task")
