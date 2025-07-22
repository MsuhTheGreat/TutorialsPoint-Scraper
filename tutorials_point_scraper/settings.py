import tutorials_point_scraper.logging_config

BOT_NAME = "tutorials_point_scraper"

SPIDER_MODULES = ["tutorials_point_scraper.spiders"]
NEWSPIDER_MODULE = "tutorials_point_scraper.spiders"

ROBOTSTXT_OBEY = False

FEEDS = {
    'data.jsonl': {'format': 'jsonl', 'overwrite': True}
    }

LOG_STDOUT = True
LOG_LEVEL = "DEBUG"
LOG_FILE = "scrapy_log.log"
LOG_FILE_APPEND = False
# LOG_FORMAT = '%(asctime)s [%(levelname)s] %(message)s'

CONCURRENT_REQUESTS = 32

TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

DOWNLOAD_DELAY = 0  # wait 2 seconds between requests
# RANDOMIZE_DOWNLOAD_DELAY = True  # make it more human-like
CONCURRENT_REQUESTS_PER_DOMAIN = 32

