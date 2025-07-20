import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(name)s. %(asctime)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger("App test rest")
