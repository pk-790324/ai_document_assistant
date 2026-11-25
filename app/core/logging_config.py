
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Create logs directory in project root
BASE_DIR = Path(__file__).resolve().parents[2]
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "app.log"

# Log format
LOG_FORMAT = (
    "%(asctime)s | %(levelname)s | "
    "%(name)s | %(message)s"
)

def setup_logging():

    formatter = logging.Formatter(LOG_FORMAT)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # File handler with rotation
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=3,
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)

    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        handlers=[
            console_handler,
            file_handler
        ],
        force=True
    )
