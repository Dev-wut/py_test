import logging
import os
import json
from typing import List, Optional

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
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)

def load_scraper_config():
    """
    Loads the scraper configuration from a JSON file.
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(SCRAPER_CONFIG_FILE):
        logging.warning(f"Scraper config file not found: {SCRAPER_CONFIG_FILE}. Using default values.")
        # Return a default config if the file doesn't exist
        return {
            "base_url": "https://www.priceza.com",
            "selectors": {
                "load_more_button": { "class": "hotdeal-tab__load-more__btn" },
                "hot_deals_container": { "tag": "div", "class": "pz-pdb-section", "id": "home-specials" },
                "product_item": { "tag": "div", "class": "pz-pdb-item" },
                "title": { "tag": "h3", "class": "pz-pdb_name" },
                "original_price": { "tag": "del", "class": "pz-base-price" },
                "price": { "tag": "span", "class": "pz-pdb-price" },
                "discount": { "tag": "div", "class": "pz-label--discount" },
                "image": { "tag": "img", "class": "pz-pdb_media--img" },
                "merchant_image": { "tag": "img", "class": "pz-pdb_store--img" },
                "product_link": { "tag": "a", "attrs": { "href": True, "onmousedown": True } },
                "rating": { "tag": "div", "class": "pz-rating-score-text" }
            },
            "json_keys": {
                "title": "title",
                "price": "price",
                "original_price": "original_price",
                "discount": "discount",
                "image_url": "image_url",
                "product_url": "product_url",
                "merchant": "merchant",
                "merchant_image": "merchant_image",
                "rating": "rating",
                "reviews_count": "reviews_count"
            }
        }
    try:
        with open(SCRAPER_CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Failed to load scraper config file: {e}. Using default values.")
        return {
            "base_url": "https://www.priceza.com",
            "selectors": {
                "load_more_button": { "class": "hotdeal-tab__load-more__btn" },
                "hot_deals_container": { "tag": "div", "class": "pz-pdb-section", "id": "home-specials" },
                "product_item": { "tag": "div", "class": "pz-pdb-item" },
                "title": { "tag": "h3", "class": "pz-pdb_name" },
                "original_price": { "tag": "del", "class": "pz-base-price" },
                "price": { "tag": "span", "class": "pz-pdb-price" },
                "discount": { "tag": "div", "class": "pz-label--discount" },
                "image": { "tag": "img", "class": "pz-pdb_media--img" },
                "merchant_image": { "tag": "img", "class": "pz-pdb_store--img" },
                "product_link": { "tag": "a", "attrs": { "href": True, "onmousedown": True } },
                "rating": { "tag": "div", "class": "pz-rating-score-text" }
            },
            "json_keys": {
                "title": "title",
                "price": "price",
                "original_price": "original_price",
                "discount": "discount",
                "image_url": "image_url",
                "product_url": "product_url",
                "merchant": "merchant",
                "merchant_image": "merchant_image",
                "rating": "rating",
                "reviews_count": "reviews_count"
            }
        }

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