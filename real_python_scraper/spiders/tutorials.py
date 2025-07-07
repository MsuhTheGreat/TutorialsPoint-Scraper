import scrapy
from real_python_scraper.items import RealPythonItem
from trafilatura import extract_metadata
import httpx
import random


SCRAPEOPS_ENDPOINT = 'https://headers.scrapeops.io/v1/browser-headers'
WEBSHARE_API_KEY = "f23s4fccj3lflqp7dez3nijprk3tgkuofh58grus"
SCRAPEOPS_API_KEY = '7be29637-7ac6-4b9c-a168-985cf51ddbfe'


def get_scrapeops_headers():
    with httpx.Client(timeout=15) as client:
        params = {'api_key': SCRAPEOPS_API_KEY, 'num_results': 50}
        response = client.get(SCRAPEOPS_ENDPOINT, params=params)
        return response.json().get("result", [])


def get_webshare_proxies():
    headers = {
        "Authorization": f"Token {WEBSHARE_API_KEY}"
    }
    url = "https://proxy.webshare.io/api/v2/proxy/list/?mode=direct"
    with httpx.Client(timeout=15) as client:
        response = client.get(url, headers=headers)
        data = response.json()
    proxy_list = [f'http://{result["username"]}:{result["password"]}@{result["proxy_address"]}:{result["port"]}' for result in data['results']]
    return proxy_list


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
        'list_of_contents': '//div[contains(@class, "article-body")]//div[contains(@class, "toc")]/ul/li',
        'publish_date': '//div[contains(@class, "mb-0")]//span[contains(@class, "text-muted")]/text()[normalize-space()]',
        'next_page': '//ul[contains(@class, "pagination")]/li[@class="page-item"][last()]/a/@href'
    }


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.headers_list = get_scrapeops_headers()
        self.proxy_list = get_webshare_proxies()
    
    
    def start_requests(self):
        for category in self.categories:
            url = "https://realpython.com/tutorials/" + category
            yield scrapy.Request(
                url,
                callback=self.parse_tutorials,
                headers=random.choice(self.headers_list),
                meta={'proxy': random.choice(self.proxy_list)}
            )


    def parse_tutorials(self, response):
        tutorials = response.xpath(self.selectors["tutorials"])
        for tutorial in tutorials:
            tutorial_url = tutorial.xpath(self.selectors["url"]).get()
            if tutorial_url:
                unwanted_keywords = ["podcast", "quiz", "course", "quizzes", "podcasts", "courses"]
                if not any(word in tutorial_url for word in unwanted_keywords):
                    yield response.follow(
                    tutorial_url,
                    callback=self.parse_page,
                    headers=random.choice(self.headers_list),
                    meta={'proxy': random.choice(self.proxy_list)}
                    )

        next_page = response.xpath(self.selectors["next_page"]).get(default=None)
        if next_page:
            yield response.follow(
                next_page,
                callback=self.parse_tutorials,
                headers=random.choice(self.headers_list),
                meta={'proxy': random.choice(self.proxy_list)}
            )
    

    def parse_page(self, response):
        real_python_item = RealPythonItem()
        
        real_python_item["title"]            = response.xpath(self.selectors["title"]).get(default=None)
        real_python_item["author"]           = response.xpath(self.selectors["author"]).get(default=None)
        real_python_item["publish_date"]     = response.xpath(self.selectors["publish_date"]).getall()
        real_python_item["summary"]          = self.get_summary(response)
        real_python_item["list_of_contents"] = self.list_of_contents(response, self.selectors["list_of_contents"])
        real_python_item["tags"]             = response.xpath(self.selectors["tags"]).getall()
        real_python_item["url"]              = response.url

        yield real_python_item
    

    def list_of_contents(self, response, li_elements_selector):
        lst = []
        li_elements = response.xpath(li_elements_selector)
        for li_element in li_elements:
            lst.append(li_element.xpath('./a/text()').get(default=None))
            if li_element.xpath('./ul'):
                sub_li_elements = li_element.xpath('./ul/li')
                for sub_li_element in sub_li_elements:
                    result = sub_li_element.xpath('./a/text()').get(default=None)
                    if result:
                        lst.append(f"\t{result}")
        return lst
    

    def get_summary(self, response):
        html = response.text
        metadata = extract_metadata(html)
        if metadata and metadata.description:
            return metadata.description.strip()
        return None
    

