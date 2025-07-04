import scrapy


class TutorialsSpider(scrapy.Spider):
    name = "tutorials"
    allowed_domains = ["realpython.com"]
    categories = ["basic", "intermediate", "advanced"]
    selectors = {
        'tutorials': '//div[contains(@class, "col-12") or contains(@class, "col-md-6") or contains(@class, "mb-5")]',
        'url': './/div[contains(@class, "card-body") or contains(@class, "m-0") or contains(@class, "p-0") or contains(@class, "mt-2")]//a/@href',
        'title': '//div[contains(@class, "col-md-11") or contains(@class, "col-lg-8") or contains(@class, "article") or contains(@class, "with-headerlinks")]//h1/text()',
        'author': '//div[contains(@class, "mb-0")]/span[contains(@class, "text-muted")]/a[contains(@class, "text-muted") and contains(@href, "#author")]/text()',
        'tags': '//span[contains(@class, "d-inline") or contains(@class, "d-md-block")]/a[contains(@class, "badge") or contains(@class, "badge-light") or contains(@class, "text-muted")]/text()',
        'table_of_contents': '//div[contains(@class, "toc")]/ul/li',

    }


    async def start(self, response):
        for category in self.categories:
            url = "https://realpython.com/tutorials/" + category
            yield response.follow(url, callback=self.parse)


    def parse_tutorials(self, response):
        tutorials = response.xpath(self.selectors["tutorials"])
        for tutorial in tutorials:
            tutorial_url = tutorial.xpath(self.selectors["url"]).get()
            yield response.follow(tutorial_url, callback=self.parse_page)
    

    def parse_page(self, response):
        ...