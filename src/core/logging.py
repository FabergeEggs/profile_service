import logging
import sys

from src.core.config import settings


def setup_logging() -> logging.Logger:
    log_format = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    level_name = getattr(settings, "log_level", "INFO")
    level = getattr(logging, str(level_name).upper(), logging.INFO)

    logging.basicConfig(
        level=level,
        format=log_format,
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,
    )

    for noisy in ("httpx", "httpcore", "aiokafka", "sqlalchemy.engine"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    return logging.getLogger("profile_service")
