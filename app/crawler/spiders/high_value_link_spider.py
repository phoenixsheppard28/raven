import scrapy
from scrapy.http import HtmlResponse
from openai import OpenAI
from internal.secrets import settings
import mimetypes
from urllib.parse import urljoin
import trafilatura
from scrapy.spiders import CrawlSpider


# ! fix this entire file


class HighValueLinkSpider(CrawlSpider):
    name = "high_value_link_spider"
    

    custom_settings  = {
        'ITEM_PIPELINES': {
            'crawler.pipelines.ResultCollectorPipeline': 100,
        },
        'DEPTH_LIMIT': 2,
        'DOWNLOAD_DELAY': 0.5,
        'ROBOTSTXT_OBEY': True,
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        # 'LOG_LEVEL':'CRITICAL'
    }

    def __init__(self, start_url, target_keywords=None, *args, **kwargs):
        self.start_urls = [start_url] # maybe it can do multiple at a time? or would it be better 1 per celery task 
        self.chat_client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.target_keywords = target_keywords 
        super(HighValueLinkSpider,self).__init__(**kwargs)


    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response: HtmlResponse):
        links = response.css('a::attr(href)').getall()
        for link in links:
            # handle relative links?
            if any(link.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.css', '.js']):
                continue
            absolute_link = urljoin(response.url, link)
            yield scrapy.Request(url=absolute_link, callback=self.parse_link)
           

    def parse_link(self, response: HtmlResponse):
        
        extracted_text = trafilatura.extract(response.text)
        text = extracted_text  # [:5000] # cap text if needed, but the model im using is so cheap it doesnt matter 
        relevance_score = self.rank_relevance(text)
        yield {
            "url": response.url,
            "relevance_score": relevance_score,
            "file_type": self.guess_file_type(response),
            "keywords": self.extract_keywords(text),
            "text":text
        }

    def rank_relevance(self, text):
        prompt = (
        f"Given the following text, rate its relevance to these keywords: {self.target_keywords}.\n"
        "Return ONLY a single float number between 1 and 10, where 10 is most relevant and 1 is least relevant.\n"
        f"Text: {text}" # maybe give it an example
        )
        response = self.chat_client.chat.completions.create(
            model="gpt-4.1-nano",
            messages=[
            {"role": "system", "content": "You are a helpful assistant that ONLY returns a float between 1 and 10, and never any explanation. \
             Here is an example of a 1/10 relevance score text: . \
             Here is an example of a 10/10 relevance score text: ."},
            {"role": "user", "content": prompt}
            ],
            max_tokens=17
        )
        return float(response.choices[0].message.content.strip()) if response.choices else -1.0 #placeholder 

    def extract_keywords(self, text): 
        return [kw for kw in self.target_keywords if kw.lower() in text.lower()]
    
    def guess_file_type(self,response: HtmlResponse):
        file_type, encoding = mimetypes.guess_type(response.url)
        return file_type or "unknown"