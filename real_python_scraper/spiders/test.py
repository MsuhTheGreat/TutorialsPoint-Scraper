import scrapy
import trafilatura
import random
import httpx

SCRAPEOPS_API_KEY = '7be29637-7ac6-4b9c-a168-985cf51ddbfe'
WEBSHARE_API_KEY = 'f23s4fccj3lflqp7dez3nijprk3tgkuofh58grus'


def get_scrapeops_headers():
    with httpx.Client(timeout=15) as client:
        params = {'api_key': SCRAPEOPS_API_KEY, 'num_results': 50}
        response = client.get('https://headers.scrapeops.io/v1/browser-headers', params=params)
        return response.json().get("result", [])


def get_webshare_proxies():
    headers = {"Authorization": f"Token {WEBSHARE_API_KEY}"}
    with httpx.Client(timeout=15) as client:
        response = client.get("https://proxy.webshare.io/api/v2/proxy/list/?mode=direct", headers=headers)
        data = response.json()
    return [f'http://{result["username"]}:{result["password"]}@{result["proxy_address"]}:{result["port"]}' for result in data['results']]


class TutorialsSpider(scrapy.Spider):
    name = "test"
    allowed_domains = ["tutorialspoint.com"]
    start_urls = ["https://www.tutorialspoint.com/python"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.headers_list = get_scrapeops_headers()
        self.proxy_list = get_webshare_proxies()
        self.sections = []

    def parse(self, response):
        section = None
        # Fix xpath: contains() must be inside [], use 'and' for multiple classes
        chapters = response.xpath('//ul[contains(@class, "toc") or contains(@class, "chapters")]/li')

        for chapter in chapters:
            # Fixed xpath: contains() inside [] and correct usage for class matching
            is_heading = chapter.xpath('contains(@class, "heading")').get()
            if is_heading:
                title = chapter.xpath('text()').get()
                section = {
                    "title": title.strip() if title else "Untitled Section",
                    "pages": []
                }
                self.sections.append(section)
            else:
                url = chapter.xpath('./a/@href').get()
                if not url:
                    self.logger.warning("🚨 URL NOT FOUND for chapter: %s", chapter.get())
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
        html = response.text
        url = response.url

        metadata = trafilatura.extract_metadata(html, url=url) or {}
        toc = self.extract_headings_with_hierarchy(response)

        yield {
            "url": url,
            "title": metadata.get("title"),
            "author": metadata.get("author"),
            "date": metadata.get("date"),
            "tags": metadata.get("tags"),
            "summary": metadata.get("summary"),
            "table_of_contents": toc
        }

    def extract_headings_with_hierarchy(self, response):
        """
        Extract all h1-h6 headings under #mainContent with nested hierarchy,
        using Scrapy selectors and stack logic for correct nesting.
        """
        headings = response.xpath('//*[@id="mainContent"]//*[self::h1 or self::h2 or self::h3 or self::h4 or self::h5 or self::h6]')

        hierarchy = []
        stack = []

        for tag in headings:
            text = tag.xpath('normalize-space()').get()
            tag_name = tag.root.tag
            level = int(tag_name[1])  # h2 -> 2

            heading_data = {
                "heading": text,
                "level": level,
                "sub_headings": []
            }

            # Pop stack until the current heading can be nested under the correct parent
            while stack and stack[-1]["level"] >= level:
                stack.pop()

            if not stack:
                hierarchy.append(heading_data)
            else:
                stack[-1]["sub_headings"].append(heading_data)

            stack.append(heading_data)

        return hierarchy
