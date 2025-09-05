
import logging
import os
from typing import List, Optional
from copy import deepcopy

from config import DEFAULT_SCRAPER_CONFIG
from utils.logging import setup_logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# --- Configuration ---
LOG_FILE = "priceza_scraper.log"
DATA_DIR = "data"
LATEST_DEALS_FILE = os.path.join(DATA_DIR, "latest_deals.json")
SCRAPER_STATUS_FILE = os.path.join(DATA_DIR, "scraper_status.json")
SCRAPER_CONFIG_FILE = os.path.join(DATA_DIR, "scraper_config.json")

# --- Logging Setup ---
setup_logging(LOG_FILE)

# --- FastAPI App Initialization ---
app = FastAPI(
    title="PriceZA Scraper API",
    description="An API to scrape hot deals from Priceza and view the results.",
    version="1.0.0",
)

# --- CORS Middleware ---
# Allow requests from typical frontend development servers
origins = [
    "http://localhost",
    "http://localhost:3000",  # Default for React
    "http://localhost:5173",  # Default for Vite + React
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)





# --- API Models ---



class SelectorDetail(BaseModel):
    tag: Optional[str] = None
    class_name: Optional[str] = Field(None, alias="class") # Use alias for 'class' keyword
    id: Optional[str] = None
    attrs: Optional[dict] = None

class SelectorConfig(BaseModel):
    load_more_button: SelectorDetail
    hot_deals_container: SelectorDetail
    product_item: SelectorDetail
    title: SelectorDetail
    original_price: SelectorDetail
    price: SelectorDetail
    discount: SelectorDetail
    image: SelectorDetail
    merchant_image: SelectorDetail
    product_link: SelectorDetail
    rating: SelectorDetail

class JsonKeysConfig(BaseModel):
    title: str
    price: str
    original_price: str
    discount: str
    image_url: str
    product_url: str
    merchant: str
    merchant_image: str
    rating: str
    reviews_count: str

class ScraperConfig(BaseModel):
    base_url: str
    selectors: SelectorConfig
    json_keys: JsonKeysConfig

class ScraperStatus(BaseModel):
    is_scraping: bool

class Deal(BaseModel):
    """Defines the structure of a single deal for the API response."""
    title: str
    price: str
    original_price: Optional[str] = ""
    discount: Optional[str] = ""
    image_url: Optional[str] = ""
    product_url: Optional[str] = ""
    merchant: Optional[str] = ""
    merchant_image: Optional[str] = ""
    rating: Optional[str] = ""
    reviews_count: Optional[str] = ""


class ScrapeResponse(BaseModel):
    """Defines the structure of the response for the deals endpoint."""
    timestamp: str
    total_products: int
    products: List[Deal]


# --- API Endpoints ---
@app.get(
    "/api/scraper_config",
    response_model=ScraperConfig,
    summary="Get Scraper Configuration",
    description="Retrieves the current configuration used by the scraper.",
)
def get_scraper_config():
    """
    Reads the scraper configuration from the JSON file and returns it.
    If the file doesn't exist, it returns a default configuration.
    """
    if not os.path.exists(SCRAPER_CONFIG_FILE):
        # Initialize with default config if the file doesn't exist
        try:
            os.makedirs(DATA_DIR, exist_ok=True)
            with open(SCRAPER_CONFIG_FILE, "w", encoding="utf-8") as f:
                import json
                json.dump(DEFAULT_SCRAPER_CONFIG, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logging.error(f"Failed to initialize {SCRAPER_CONFIG_FILE}: {e}")
        return deepcopy(DEFAULT_SCRAPER_CONFIG)

    try:
        with open(SCRAPER_CONFIG_FILE, "r", encoding="utf-8") as f:
            import json
            data = json.load(f)
        return data
    except Exception as e:
        logging.error(f"Could not read or parse {SCRAPER_CONFIG_FILE}: {e}")
        # Return default config on error as well
        return deepcopy(DEFAULT_SCRAPER_CONFIG)

@app.post(
    "/api/scraper_config",
    summary="Update Scraper Configuration",
    description="Updates the scraper configuration. This will take effect on the next scrape.",
)
def update_scraper_config(config: ScraperConfig):
    """
    Writes the provided scraper configuration to the JSON file.
    """
    try:
        with open(SCRAPER_CONFIG_FILE, "w", encoding="utf-8") as f:
            import json
            json.dump(config.dict(by_alias=True), f, ensure_ascii=False, indent=2)
        logging.info("Scraper configuration updated successfully.")
        return {"message": "Scraper configuration updated successfully."}
    except Exception as e:
        logging.error(f"Failed to write scraper configuration file: {e}")
        return {"message": f"Failed to update scraper configuration: {e}"}

@app.get(
    "/api/scraper_status",
    response_model=ScraperStatus,
    summary="Get Scraper Status",
    description="Retrieves the current status of the scraper (e.g., if it's currently scraping).",
)
def get_scraper_status():
    """
    Reads the scraper status from the JSON file and returns it.
    If the file doesn't exist, it returns a default status of not scraping.
    """
    if not os.path.exists(SCRAPER_STATUS_FILE):
        return {"is_scraping": False}

    try:
        with open(SCRAPER_STATUS_FILE, "r", encoding="utf-8") as f:
            import json
            data = json.load(f)
        return data
    except Exception as e:
        logging.error(f"Could not read or parse {SCRAPER_STATUS_FILE}: {e}")
        return {"is_scraping": False}

@app.get(
    "/api/deals",
    response_model=ScrapeResponse,
    summary="Get Latest Scraped Deals",
    description="Retrieves the most recently scraped hot deals from the persistent JSON file.",
)
def get_latest_deals():
    """
    Reads the latest deals from the JSON file and returns them.
    If the file doesn't exist, it returns an empty list.
    """
    if not os.path.exists(LATEST_DEALS_FILE):
        return {"timestamp": "", "total_products": 0, "products": []}

    try:
        with open(LATEST_DEALS_FILE, "r", encoding="utf-8") as f:
            import json
            data = json.load(f)
        return data
    except Exception as e:
        logging.error(f"Could not read or parse {LATEST_DEALS_FILE}: {e}")
        return {"timestamp": "", "total_products": 0, "products": []}





@app.get("/", include_in_schema=False)
def root():
    return {"message": "PriceZA Scraper API is running. Visit /docs for API documentation."}

