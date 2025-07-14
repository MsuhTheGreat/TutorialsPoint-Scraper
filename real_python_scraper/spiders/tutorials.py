import scrapy
from real_python_scraper.items import RealPythonItem
from trafilatura import extract_metadata
import httpx
import random
from html_to_markdown import convert_to_markdown


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
    allowed_domains = ["tutorialspoint.com"]
    url_selector = '//ul[contains(@class, "toc") or contains(@class, "chapters")]/li'
    headers_list = get_scrapeops_headers()
    proxy_list = get_webshare_proxies()
    sections = []


    async def start(self):
        url = "https://www.tutorialspoint.com/python"
        yield scrapy.Request(
            url = url,
            callback=self.collect_urls,
            headers=random.choice(self.headers_list),
            meta={"proxy": random.choice(self.proxy_list)}
        )
    

    def collect_urls(self, response):
        section = None
        chapters = response.xpath(self.url_selector)

        for chapter in chapters:
            if chapter.xpath('contains(@class, "heading")'):
                section = {
                    "title": chapter.xpath('/text()'),
                    "pages": []
                }
                self.sections.append(section)
            else:
                url = chapter.xpath('./a/@href').get()
                if url: 
                    url = 'https://www.tutorialspoint.com' + url
                else:
                    print("🚨 URL NOT FOUND")
                    continue
                if section is None:
                    section = {
                            "title": "Introduction To Python",
                            "pages": []
                        }
                    self.sections.append(section)
                section["pages"].append({"url": url})
        
        self.prepare_raw_data()
        

    def prepare_raw_data(self):
        for section in self.sections:
            for page in section["pages"]:
                url = page["url"]
                response = yield scrapy.Request(
                    url = url,
                    headers=random.choice(self.headers_list),
                    meta={"proxy": random.choice(self.proxy_list)}
                )                
                html = response.xpath('//div[@id="mainContent"]')
                markdown = convert_to_markdown(html)
                page["raw_data"] = markdown
    

    def get_cleaned_data(self):
        ...
