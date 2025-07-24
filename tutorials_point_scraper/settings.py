"""
Scrapy Settings
----------------
Configuration for the TutorialsPoint Scraper.

Features:
- Feed export to JSON with UTF-8 encoding.
- Disables robots.txt.
- Custom logging configuration.
"""

import tutorials_point_scraper.logging_config

# Name of the bot
BOT_NAME = "tutorials_point_scraper"

# Location of spider modules
SPIDER_MODULES = ["tutorials_point_scraper.spiders"]
NEWSPIDER_MODULE = "tutorials_point_scraper.spiders"

# Disable obeying robots.txt
ROBOTSTXT_OBEY = False

# Configure output feed
FEEDS = {
    'output/tutorials.jsonl': {
        'format': 'jsonlines',
        'encoding': 'utf8',
        'overwrite': True,
    }
}

CONCURRENT_REQUESTS = 32

TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

DOWNLOAD_DELAY = 0
CONCURRENT_REQUESTS_PER_DOMAIN = 32

