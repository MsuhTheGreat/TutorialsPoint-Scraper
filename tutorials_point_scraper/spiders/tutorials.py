import scrapy
import trafilatura
import random
import httpx
import os
from dotenv import load_dotenv
from tutorials_point_scraper.items import TutorialsPointItem
import json

load_dotenv()

SCRAPEOPS_API_KEY = os.getenv("SCRAPEOPS_API_KEY", "")
WEBSHARE_API_KEY = os.getenv("WEBSHARE_API_KEY", "")
HTTPX_CLIENT_TIMEOUT = 15


def get_scrapeops_headers():
    with httpx.Client(timeout=HTTPX_CLIENT_TIMEOUT) as client:
        params = {'api_key': SCRAPEOPS_API_KEY, 'num_results': 50}
        response = client.get('https://headers.scrapeops.io/v1/browser-headers', params=params)
        return response.json().get("result", [])


def get_webshare_proxies():
    headers = {"Authorization": f"Token {WEBSHARE_API_KEY}"}
    with httpx.Client(timeout=HTTPX_CLIENT_TIMEOUT) as client:
        response = client.get("https://proxy.webshare.io/api/v2/proxy/list/?mode=direct", headers=headers)
        data = response.json()
    return [f'http://{result["username"]}:{result["password"]}@{result["proxy_address"]}:{result["port"]}' for result in data['results']]


class TutorialsSpider(scrapy.Spider):
    name = "tutorials"
    allowed_domains = ["tutorialspoint.com"]
    start_urls = ["https://www.tutorialspoint.com/python"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.headers_list = get_scrapeops_headers()
        self.proxy_list = get_webshare_proxies()
        self.sections = []

    def parse(self, response):
        section = None
        chapters = response.xpath('//ul[contains(@class, "toc") and contains(@class, "chapters")]/li')

        for chapter in chapters:
            classes = chapter.attrib.get('class', '')

            if 'heading' in classes.split():
                title = chapter.xpath('normalize-space(text())').get()
                section = {
                    "title": title.strip() if title else "Untitled Section",
                    "pages": []
                }
                self.sections.append(section)
            else:
                url = chapter.xpath('./a/@href').get()
                if not url:
                    self.logger.warning(f"🚨 URL NOT FOUND for chapter: {chapter.get()}")
                    continue
                full_url = response.urljoin(url)

                if section is None:
                    section = {
                        "title": "Introduction to Python",
                        "pages": []
                    }
                    self.sections.append(section)
                section["pages"].append({"url": full_url})

                yield scrapy.Request(
                    url=full_url,
                    callback=self.parse_blog_page,
                    headers=random.choice(self.headers_list),
                    meta={"proxy": random.choice(self.proxy_list)}
                )


    def parse_blog_page(self, response):
        tutorials_point_item = TutorialsPointItem()
        html = response.text
        url = response.url

        metadata = trafilatura.extract_metadata(html)
        
        if metadata: metadata = metadata.as_dict()
        else: metadata = {}
        
        toc = self.extract_headings_with_hierarchy(response)

        tutorials_point_item["url"]              = url
        tutorials_point_item["title"]            = metadata.get("title")
        tutorials_point_item["author"]           = metadata.get("author")
        tutorials_point_item["publish_date"]     = metadata.get("date")
        tutorials_point_item["tags"]             = metadata.get("tags")
        tutorials_point_item["summary"]          = metadata.get("summary")
        tutorials_point_item["list_of_contents"] = toc

        self.logger.info(json.dumps(dict(tutorials_point_item), ensure_ascii=False))
        self.logger.debug(json.dumps(dict(tutorials_point_item), ensure_ascii=False))
        yield tutorials_point_item


    def extract_headings_with_hierarchy(self, response):
        headings = response.xpath('//*[@id="mainContent"]//*[self::h1 or self::h2 or self::h3 or self::h4 or self::h5 or self::h6]')

        hierarchy = []
        stack = []

        for tag in headings:
            text = tag.xpath('normalize-space()').get()
            tag_name = tag.root.tag
            level = int(tag_name[1])

            heading_data = {
                "heading": text,
                "level": level,
                "sub_headings": []
            }

            while stack and stack[-1]["level"] >= level:
                stack.pop()

            if not stack:
                hierarchy.append(heading_data)
            else:
                stack[-1]["sub_headings"].append(heading_data)

            stack.append(heading_data)

        return hierarchy
