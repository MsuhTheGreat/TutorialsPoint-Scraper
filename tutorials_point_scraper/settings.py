BOT_NAME = "tutorials_point_scraper"

SPIDER_MODULES = ["tutorials_point_scraper.spiders"]
NEWSPIDER_MODULE = "tutorials_point_scraper.spiders"

ROBOTSTXT_OBEY = False

LOG_ENABLED = True
# LOG_LEVEL = 'ERROR'
LOG_FILE = 'scrapy_log.log'
FEEDS = {
    'data.jsonl': {'format': 'jsonl', 'overwrite': True}
    }

CONCURRENT_REQUESTS = 32

TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

DOWNLOAD_DELAY = 0  # wait 2 seconds between requests
# RANDOMIZE_DOWNLOAD_DELAY = True  # make it more human-like
CONCURRENT_REQUESTS_PER_DOMAIN = 32

