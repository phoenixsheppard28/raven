from crawler.spiders.high_value_link_spider import HighValueLinkSpider
from scrapy.crawler import CrawlerProcess
from scrapy.signalmanager import dispatcher
from scrapy import signals



def run_spider(start_url:str,target_keywords:list): #spider abstraction for the celery task to use 

    spider_settings = {
    'ITEM_PIPELINES': {
        'crawler.pipelines.ResultCollectorPipeline': 100,
    },
    'DEPTH_LIMIT': 2,
    'DOWNLOAD_DELAY': 0.5,
    'ROBOTSTXT_OBEY': True,
    'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }


    process = CrawlerProcess(settings=spider_settings)
    results = [] # simple list to hold our scraping results 

    def crawler_results(spider):
        if hasattr(spider, 'collected_items'):
            results.extend(spider.collected_items)



    dispatcher.connect(crawler_results, signal=signals.spider_closed)

    process.crawl(HighValueLinkSpider,start_url=start_url,target_keywords=target_keywords)


    process.start()

    return results