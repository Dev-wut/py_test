
import logging
import os
from typing import List, Optional
from copy import deepcopy

try:
    from .config import DEFAULT_SCRAPER_CONFIG
except ImportError:  # pragma: no cover
    from config import DEFAULT_SCRAPER_CONFIG
try:
    from .utils.logging import setup_logging
    from .database import get_deals_from_db, get_all_merchants, create_tables
except ImportError:  # pragma: no cover
    from utils.logging import setup_logging
    from database import get_deals_from_db, get_all_merchants, create_tables

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ConfigDict

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

@app.on_event("startup")
def startup_event():
    create_tables()

# --- CORS Middleware ---
# Allow requests based on the ALLOWED_ORIGINS environment variable.
# Use a safe default and warn if the variable is not provided.
origins_env = os.getenv("ALLOWED_ORIGINS")
if origins_env:
    origins = [origin.strip() for origin in origins_env.split(",") if origin.strip()]
else:
    origins = ["http://localhost"]
    logging.error(
        "ALLOWED_ORIGINS not set; defaulting to ['http://localhost']. "
        "Set ALLOWED_ORIGINS environment variable in production."
    )
allow_credentials = True
if origins == ["*"]:
    allow_credentials = False
    logging.warning(
        "ALLOWED_ORIGINS set to '*' – allowing all origins without credentials."
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)





# --- API Models ---



class SelectorDetail(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    tag: Optional[str] = None
    class_name: Optional[str] = Field(None, alias="class")  # Use alias for 'class' keyword
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
    total_products: int
    products: List[Deal]
    page: int
    page_size: int


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
    description="Retrieves the most recently scraped hot deals from the database with pagination.",
)
def get_latest_deals(page: int = 1, page_size: int = 50, merchant: Optional[str] = None):
    """
    Reads the latest deals from the database with pagination.
    """
    try:
        deals_data = get_deals_from_db(page, page_size, merchant)
        return deals_data
    except Exception as e:
        logging.error(f"Could not fetch deals from database: {e}")
        return {"total_products": 0, "products": [], "page": page, "page_size": page_size}

@app.get("/api/merchants", response_model=List[str], summary="Get All Merchants")
def get_all_merchants_api():
    """
    Retrieves a list of all unique merchant names from the database.
    """
    try:
        merchants = get_all_merchants()
        return merchants
    except Exception as e:
        logging.error(f"Could not fetch merchants from database: {e}")
        return []





import httpx
from fastapi.responses import StreamingResponse

@app.get("/api/proxy-image")
async def proxy_image(url: str):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            return StreamingResponse(response.iter_bytes(), media_type=response.headers.get("content-type"))
        except httpx.HTTPStatusError as e:
            logging.error(f"Failed to fetch image from {url}: {e}")
            return {"message": "Failed to fetch image"}, 400

@app.get("/", include_in_schema=False)
def root():
    return {"message": "PriceZA Scraper API is running. Visit /docs for API documentation."}

