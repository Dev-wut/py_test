import logging
from typing import Optional


def setup_logging(log_file: Optional[str] = "priceza_scraper.log") -> None:
    """Configure basic logging for the application.

    Parameters
    ----------
    log_file: Optional[str]
        The path to the log file. Defaults to "priceza_scraper.log".
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )
