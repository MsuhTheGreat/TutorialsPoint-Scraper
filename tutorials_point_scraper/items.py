"""
TutorialsPoint Scraper Items
-----------------------------
Defines the fields used to collect tutorial data from TutorialsPoint.
"""

import scrapy


class TutorialsPointItem(scrapy.Item):
    title            = scrapy.Field()
    author           = scrapy.Field()
    publish_date     = scrapy.Field()
    summary          = scrapy.Field()
    tags             = scrapy.Field()
    url              = scrapy.Field()
    list_of_contents = scrapy.Field()
