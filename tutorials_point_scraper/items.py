# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class TutorialsPointItem(scrapy.Item):
    # define the fields for your item here like:
    title = scrapy.Field()
    author = scrapy.Field()
    publish_date = scrapy.Field()
    summary = scrapy.Field()
    list_of_contents = scrapy.Field()
    tags = scrapy.Field()
    url = scrapy.Field()
