import scrapy
from scrapy.http import HtmlResponse
from openai import OpenAI
from app.internal.secrets import settings
import mimetypes
from urllib.parse import urljoin
import trafilatura
from scrapy.spiders import CrawlSpider
from scrapy.utils.project import get_project_settings



# ! fix this entire file


class HighValueLinkSpider(CrawlSpider):
    name = "high_value_link_spider"
    
    spider_settings = get_project_settings()

    def __init__(self, start_url, target_keywords=None, *args, **kwargs):
        self.start_urls = [start_url] # maybe it can do multiple at a time? or would it be better 1 per celery task 
        self.chat_client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.target_keywords = target_keywords or self.spider_settings.get('DEFAULT_TARGET_KEYWORDS')
        super(HighValueLinkSpider,self).__init__(**kwargs)


    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response: HtmlResponse):
        links = response.css('a::attr(href)').getall()
        link_texts = response.css('a::text').getall()
        for link, text in zip(links, link_texts):
            if not self.should_follow_link(link, text):
                continue
            absolute_link = urljoin(response.url, link)
            yield scrapy.Request(url=absolute_link, callback=self.parse_link)
           

    def parse_link(self, response: HtmlResponse):
        
        extracted_text = trafilatura.extract(response.text)
        text = extracted_text[:4000] # cap to 4000 so it doesent overwhelm chat
        relevance_score = self.rank_relevance(text,response.url)
        yield {
            "url": response.url,
            "relevance_score": relevance_score,
            "file_type": self.guess_file_type(response),
            "keywords": self.extract_keywords(text),
            "text":text
        }

    def rank_relevance(self, text,url):
        prompt = (
        f"Given the following text and the url it came from, rate if it contains content relevant to these keywords: {self.target_keywords}.\n"
        "Return ONLY a single float number between 1 and 10, where 10 is most relevant and 1 is least relevant. NOT ALL THE TEXT HAS TO BE RELEVANT TO THE KEYWORDS, only some\n"
        f"Text: {text}\n"
        f"URL: {url}" 
        )
        response = self.chat_client.completions.create(
            model=self.spider_settings.get('GPT_MODEL'),
            prompt=prompt,
            temperature=0.2,
            max_tokens=self.spider_settings.get('GPT_MAX_TOKENS')
        )
        f = float(response.choices[0].text.strip()) if response.choices else -1.0 #placeholder
        print(f)
        return f

    def extract_keywords(self, text): 
        return [kw for kw in self.target_keywords if kw.lower() in text.lower()]
    
    def guess_file_type(self,response: HtmlResponse):
        file_type, encoding = mimetypes.guess_type(response.url)
        return file_type or "html"
    
    def should_follow_link(self, link, anchor_text):
        # skip ignored extensions
        if any(link.endswith(ext) for ext in self.spider_settings.get('IGNORED_EXTENSIONS', [])):
            return False
        if link.startswith('#') or link.startswith('mailto:') or link.startswith('tel:'):
            return False
        # skip links with certain keywords in the anchor text
        skip_words = [
            "login", "sign in", "register", "privacy", "terms", "contact", "about", "faq",
            "help", "support", "cookie", "accessibility", "sitemap", "feedback"
        ]
        if anchor_text and any(word in anchor_text.lower() for word in skip_words):
            return False
        # skip links that look like navigation or social media
        nav_patterns = ["facebook.com", "twitter.com", "linkedin.com", "instagram.com", "youtube.com"]
        if any(pattern in link for pattern in nav_patterns):
            return False
        #  skip links with lots of query params (often not content)
        if link.count('?') > 1:
            return False
        return True