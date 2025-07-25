"""
TutorialsPoint Spider
----------------------
Scrapy spider for crawling Python tutorials from TutorialsPoint.

Features:
- Uses rotating headers and proxies to mimic real users.
- Extracts chapters with structured sections and pages.
- Fetches metadata using Trafilatura.
- Extracts heading hierarchy (H1 to H6) as list of contents.

Environment Variables Required:
- SCRAPEOPS_API_KEY: For ScrapeOps Browser Headers API.
- WEBSHARE_API_KEY: For proxy rotation via Webshare.io.
"""

import scrapy
import trafilatura
import random
import httpx
import os
import sys
from dotenv import load_dotenv
from tutorials_point_scraper.items import TutorialsPointItem
from scrapy.utils.project import get_project_settings

# Load environment variables from .env file
load_dotenv()

# Get settings
settings = get_project_settings()

SCRAPEOPS_API_KEY = os.getenv("SCRAPEOPS_API_KEY", "")
WEBSHARE_API_KEY = os.getenv("WEBSHARE_API_KEY", "")
HTTPX_CLIENT_TIMEOUT = settings.get("HTTPX_CLIENT_TIMEOUT", 15)

if SCRAPEOPS_API_KEY == "":
    print("❌ No ScrapeOps API Key found. Scraper exiting.")
    sys.exit(1)
if WEBSHARE_API_KEY == "":
    print("❌ No Webshare API Key found. Scraper exiting.")
    sys.exit(1)


def get_scrapeops_headers():
    """Fetch rotating browser headers from ScrapeOps."""
    try:
        with httpx.Client(timeout=HTTPX_CLIENT_TIMEOUT) as client:
            params = {'api_key': SCRAPEOPS_API_KEY, 'num_results': 50}
            response = client.get('https://headers.scrapeops.io/v1/browser-headers', params=params)
            response.raise_for_status()
            return response.json().get("result", [])
    except httpx.HTTPStatusError as e:
        raise RuntimeError(f"❌ HTTP error from API: {e}")
    except Exception as e:
        raise RuntimeError(f"❌ Could not get browser headers from ScrapeOps. Error: {e}")


def get_webshare_proxies():
    """Fetch proxy list from Webshare.io."""
    headers = {"Authorization": f"Token {WEBSHARE_API_KEY}"}
    try:
        with httpx.Client(timeout=HTTPX_CLIENT_TIMEOUT) as client:
            response = client.get("https://proxy.webshare.io/api/v2/proxy/list/?mode=direct", headers=headers)
            response.raise_for_status()
            data = response.json()
        return [
            f'http://{result["username"]}:{result["password"]}@{result["proxy_address"]}:{result["port"]}'
            for result in data['results']
        ]
    except httpx.HTTPStatusError as e:
        raise RuntimeError(f"❌ HTTP error from API: {e}")
    except Exception as e:
        raise RuntimeError(f"❌ Could not get proxies from Webshare. Error: {e}")


class TutorialsSpider(scrapy.Spider):
    """
    Scrapy spider to extract metadata and structured content
    from the Python tutorial section on TutorialsPoint.
    """
    name = "tutorials"
    allowed_domains = ["tutorialspoint.com"]
    start_urls = ["https://www.tutorialspoint.com/python"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try: 
            self.headers_list = get_scrapeops_headers()
            if not self.headers_list: raise RuntimeError(f"❌ Could not get browser headers from ScrapeOps. Even with response code 200")
        except RuntimeError as e: 
            self.logger.error(e)
            sys.exit(1)
        try:
            self.proxy_list = get_webshare_proxies()
            if not self.proxy_list: raise RuntimeError(f"❌ Could not get proxies from Webshare. Even with response code 200")
        except Exception as e:
            self.logger.error(e)
            sys.exit(1)
        self.sections = []

    def parse(self, response):
        """
        Parse the table of contents page and schedule requests
        for individual chapter/tutorial pages.
        """
        section = None
        chapters = response.xpath('//ul[contains(@class, "toc") and contains(@class, "chapters")]/li')

        for chapter in chapters:
            classes = chapter.attrib.get('class', '')

            if 'heading' in classes.split():
                # Top-level section heading
                title = chapter.xpath('normalize-space(text())').get()
                section = {
                    "title": title.strip() if title else "Untitled Section",
                    "pages": []
                }
                self.sections.append(section)
            else:
                # Actual tutorial page link under section
                url = chapter.xpath('./a/@href').get()
                if not url:
                    self.logger.warning(f"🚨 URL NOT FOUND for chapter: {str(chapter.get())}")
                    continue

                full_url = response.urljoin(url)

                if section is None:
                    section = {
                        "title": "Introduction to Python",
                        "pages": []
                    }
                    self.sections.append(section)

                section["pages"].append({"url": full_url})

                # Scrape tutorial page with randomized headers and proxy
                yield scrapy.Request(
                    url=full_url,
                    callback=self.parse_blog_page,
                    headers=random.choice(self.headers_list),
                    meta={
                        "proxy": random.choice(self.proxy_list),
                    },
                    errback=self.errback_log
                )

    def parse_blog_page(self, response):
        """Parse and extract metadata and headings from a tutorial page."""
        tutorials_point_item = TutorialsPointItem()
        html = response.text
        url = response.url

        metadata = trafilatura.extract_metadata(html)
        metadata = metadata.as_dict() if metadata else {}

        toc = self.extract_headings_with_hierarchy(response)

        tutorials_point_item["url"]              = url
        tutorials_point_item["title"]            = metadata.get("title")
        tutorials_point_item["author"]           = metadata.get("author")
        tutorials_point_item["publish_date"]     = metadata.get("date")
        tutorials_point_item["tags"]             = metadata.get("tags")
        tutorials_point_item["summary"]          = metadata.get("summary")
        tutorials_point_item["list_of_contents"] = toc

        yield tutorials_point_item

    def extract_headings_with_hierarchy(self, response):
        """
        Extract headings (H1 to H6) from content in a hierarchical format.
        Returns a nested list of headings with levels and subheadings.
        """
        headings = response.xpath(
            '//*[@id="mainContent"]//*[self::h1 or self::h2 or self::h3 or self::h4 or self::h5 or self::h6]'
        )

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

            # Maintain parent-child hierarchy
            while stack and stack[-1]["level"] >= level:
                stack.pop()

            if not stack:
                hierarchy.append(heading_data)
            else:
                stack[-1]["sub_headings"].append(heading_data)

            stack.append(heading_data)

        return hierarchy
    
    def errback_log(self, failure):
        request = failure.request
        self.logger.warning(f"❌ Failed URL: {request.url}")
        self.logger.warning(f"🔁 Proxy used: {request.meta.get('proxy')}")
        self.logger.warning(repr(failure))

