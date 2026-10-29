import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


LOG_DIR = Path(__file__).resolve().parents[2] / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FORMAT = ("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

formatter = logging.Formatter(LOG_FORMAT)

info_handler = RotatingFileHandler(
    LOG_DIR / "info.log",
    maxBytes=5 * 1024 * 1024,
    backupCount=3,
    encoding="utf-8",
)
info_handler.setLevel(logging.INFO)
info_handler.addFilter(
    lambda record: logging.INFO <= record.levelno < logging.ERROR
)
info_handler.setFormatter(formatter)

error_handler = RotatingFileHandler(
    LOG_DIR / "error.log",
    maxBytes=5 * 1024 * 1024,
    backupCount=3,
    encoding="utf-8",
)
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(formatter)

logging.basicConfig(
    level=logging.INFO,
    handlers=[info_handler, error_handler],
    force=True,
)

logging.getLogger("app").setLevel(logging.INFO)
logging.getLogger("app").propagate = True
