import scrapy
from scrapy.http import HtmlResponse
from openai import OpenAI
from internal.secrets import settings
import mimetypes


# ! fix this entire file


class HighValueLinkSpider(scrapy.Spider):
    name = "high_value_link_spider"
    

    custom_settings  = {
        'ITEM_PIPELINES': {
            'crawler.pipelines.ResultCollectorPipeline': 100,
        },
        'DEPTH_LIMIT': 2,
        'DOWNLOAD_DELAY': 0.5,
        'ROBOTSTXT_OBEY': True,
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    def __init__(self, start_url, target_keywords=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_urls = [start_url] # maybe it can do multiple at a time? or would it be better 1 per celery task 
        self.chat_client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.target_keywords = target_keywords 


    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response: HtmlResponse):
        links = response.css('a::attr(href)').getall()
        for link in links:
            # handle relative links?
            if link.startswith(('http://', 'https://')) and not any(
                link.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.css', '.js']): # filter non document links
                yield scrapy.Request(url=link, callback=self.parse_link)
                # ? fix this stuff 

    def parse_link(self, response: HtmlResponse):
        text = response.text[:1000] # cap text 
        relevance_score = self.rank_relevance(text)
        yield {
            "url": response.url,
            "relevance_score": relevance_score,
            "file_type": self.guess_file_type(response),
            "keywords": self.extract_keywords(text)
        }

    def rank_relevance(self, text):
        response = self.chat_client.responses.create(
            model="gpt-4.1-nano",
            input=f"Rank the relevance of this text for keywords  {self.target_keywords} on a float (2 digit) scale of 1-10. \
            only output the SINGULAR resultant rank, not anything else. Just a Singular Rank: {text}",
            max_output_tokens=17
        )
        return float(response.output_text)

    def extract_keywords(self, text): #what?
        return [kw for kw in self.target_keywords if kw.lower() in text.lower()]
    
    def guess_file_type(self,response: HtmlResponse):
        file_type, encoding = mimetypes.guess_type(response.url)
        return file_type or "unknown"