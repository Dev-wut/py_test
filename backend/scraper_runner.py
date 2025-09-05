import logging
import os
import json
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import List, Optional
from copy import deepcopy

from config import DEFAULT_SCRAPER_CONFIG
from utils.logging import setup_logging

from apscheduler.schedulers.background import BackgroundScheduler

# Import the scraper class
from scraper import PriceZAScraper

# --- Configuration ---
LOG_FILE = "priceza_scraper.log"
DATA_DIR = "data"
LATEST_DEALS_FILE = os.path.join(DATA_DIR, "latest_deals.json")
SCRAPER_STATUS_FILE = os.path.join(DATA_DIR, "scraper_status.json")
SCRAPER_CONFIG_FILE = os.path.join(DATA_DIR, "scraper_config.json")
SCHEDULE_MINUTES = 30

# --- Logging Setup ---
setup_logging(LOG_FILE)

def load_scraper_config():
    """
    Loads the scraper configuration from a JSON file.
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(SCRAPER_CONFIG_FILE):
        logging.warning(
            f"Scraper config file not found: {SCRAPER_CONFIG_FILE}. Using default values."
        )
        try:
            with open(SCRAPER_CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(DEFAULT_SCRAPER_CONFIG, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logging.error(f"Failed to initialize {SCRAPER_CONFIG_FILE}: {e}")
        return deepcopy(DEFAULT_SCRAPER_CONFIG)
    try:
        with open(SCRAPER_CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logging.error(
            f"Failed to load scraper config file: {e}. Using default values."
        )
        return deepcopy(DEFAULT_SCRAPER_CONFIG)

def update_scraper_status(is_scraping: bool):
    """
    Updates the scraper status in a JSON file.
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    status = {"is_scraping": is_scraping}
    try:
        with open(SCRAPER_STATUS_FILE, "w", encoding="utf-8") as f:
            json.dump(status, f)
        logging.info(f"Scraper status updated to: {is_scraping}")
    except Exception as e:
        logging.error(f"Failed to update scraper status file: {e}")

# --- Scraper Logic ---
def scrape_and_save(allowed_merchants: Optional[List[str]] = None):
    """
    Initializes and runs the scraper, then saves the results to a JSON file.
    This function is designed to be called by the scheduler.
    It uses a try/finally block to ensure the Selenium driver is closed.
    """
    update_scraper_status(True) # Set status to true at the beginning of scrape
    logging.info(
        f"Starting scheduled scrape. Allowed merchants: {allowed_merchants or 'All'}"
    )
    # Ensure the data directory exists
    os.makedirs(DATA_DIR, exist_ok=True)

    with open(LATEST_DEALS_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": datetime.now(ZoneInfo("Asia/Bangkok")).isoformat(),
            "total_products": 0,
            "products": []
        }, f, ensure_ascii=False, indent=2)

    config = load_scraper_config() # Load config here
    scraper = PriceZAScraper(config=config, allowed_merchants=allowed_merchants)
    try:
        # Scrape deals
        hot_deals = scraper.scrape_hot_deals()

        # Save the results to the fixed file
        if hot_deals:
            scraper.save_to_json(LATEST_DEALS_FILE)
            logging.info(f"Scrape successful. {len(hot_deals)} deals saved.")
        else:
            logging.warning("Scrape completed, but no deals were found.")

    except Exception as e:
        logging.error(f"An error occurred during the scrape_and_save job: {e}")
    finally:
        # Ensure the driver is always closed to prevent resource leaks
        scraper.close_driver()
        update_scraper_status(False) # Reset status to false after scrape

# --- Scheduler Setup ---
scheduler = BackgroundScheduler(daemon=True)
scheduler.add_job(scrape_and_save, "interval", minutes=SCHEDULE_MINUTES)

if __name__ == "__main__":
    logging.info("Starting PriceZA Scraper Runner...")
    update_scraper_status(False) # Initialize status to false on startup
    # Run an initial scrape immediately so we have data
    logging.info("Performing initial data scrape...")
    scrape_and_save()
    # Start the scheduler
    scheduler.start()
    logging.info(
        f"Scheduler started. Scrape will run every {SCHEDULE_MINUTES} minutes."
    )

    try:
        # Keep the main thread alive
        while True:
            import time
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        logging.info("Scraper Runner shutting down.")
        scheduler.shutdown()
        update_scraper_status(False) # Ensure status is false on shutdown
