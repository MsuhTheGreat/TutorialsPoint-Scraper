import logging
from scrapy.utils.log import configure_logging
import os

os.makedirs("logs", exist_ok=True)

LOG_FILE = "logs/tutorials.log"
LOG_LEVEL = 'DEBUG'
LOG_ENABLED = False  # disable Scrapy’s root handler setup

configure_logging(install_root_handler=False)

# Console Handler
console_handler = logging.StreamHandler()
console_handler.setLevel(LOG_LEVEL)

console_formatter = logging.Formatter('[%(levelname)s] %(message)s')

console_handler.setFormatter(console_formatter)

# File Handler
file_handler = logging.FileHandler(LOG_FILE, mode='w', encoding='utf-8')
file_handler.setLevel(LOG_LEVEL)
file_formatter = logging.Formatter('[%(levelname)s] %(message)s')
file_handler.setFormatter(file_formatter)

# Add handlers to root logger
root_logger = logging.getLogger()
root_logger.setLevel(LOG_LEVEL)
root_logger.addHandler(console_handler)
root_logger.addHandler(file_handler)
