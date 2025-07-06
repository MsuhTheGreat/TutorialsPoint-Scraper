import scrapy
from real_python_scraper.items import RealPythonItem


class TutorialsSpider(scrapy.Spider):
    name = "tutorials"
    allowed_domains = ["realpython.com"]
    categories = ["basics", "intermediate", "advanced"]
    selectors = {
        'tutorials': '//div[contains(@class, "col-12") and contains(@class, "col-md-6") and contains(@class, "mb-5")]',
        'url': './div[contains(@class, "card")]/a/@href',
        'title': '//div[contains(@class, "col-md-11") or contains(@class, "col-lg-8") or contains(@class, "article") or contains(@class, "with-headerlinks")]//h1/text()',
        'author': '//div[contains(@class, "mb-0")]/span[contains(@class, "text-muted")]/a[contains(@class, "text-muted") and contains(@href, "#author")]/text()',
        'tags': '//span[contains(@class, "d-inline") or contains(@class, "d-md-block")]/a[contains(@class, "badge") or contains(@class, "badge-light") or contains(@class, "text-muted")]/text()',
        'list_of_contents': '//div[contains(@class, "toc")]/ul/li/a/text()',
        'summary': '//div[contains(@class, "article-body")]//p[1]',
        'publish_date': '//div[contains(@class, "mb-0")]//span[contains(@class, "text-muted")]/text()[normalize-space()]',
        'next_page': '//ul[contains(@class, "pagination")]/li[@class="page-item"][last()]/a/@href'
    }


    def start_requests(self):
        for category in self.categories:
            url = "https://realpython.com/tutorials/" + category
            yield scrapy.Request(url, callback=self.parse_tutorials)


    def parse_tutorials(self, response):
        tutorials = response.xpath(self.selectors["tutorials"])
        for tutorial in tutorials:
            tutorial_url = tutorial.xpath(self.selectors["url"]).get()
            for item in ["podcast", "quiz"]:
                if item not in tutorial_url:
                    yield response.follow(tutorial_url, callback=self.parse_page)
        next_page = response.xpath(self.selectors["next_page"]).get(default=None)
        if next_page:
            yield response.follow(next_page, callback=self.parse_tutorials)
    

    def parse_page(self, response):
        real_python_item = RealPythonItem()
        
        real_python_item["title"]            = response.xpath(self.selectors["title"]).get(default=None)
        real_python_item["author"]           = response.xpath(self.selectors["author"]).get(default=None)
        real_python_item["publish_date"]     = response.xpath(self.selectors["publish_date"]).getall()
        real_python_item["summary"]          = response.xpath(self.selectors["summary"]).xpath(".//text() | .//code/text()").getall()
        real_python_item["list_of_contents"] = response.xpath(self.selectors["list_of_contents"]).getall()
        real_python_item["tags"]             = response.xpath(self.selectors["tags"]).getall()
        real_python_item["url"]              = response.url

        yield real_python_item
    