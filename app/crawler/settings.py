BOT_NAME = 'crawler'
SPIDER_MODULES = ['crawler.spiders']
NEWSPIDER_MODULE = 'crawler.spiders'
ITEM_PIPELINES = {
    'crawler.pipelines.ResultCollectorPipeline': 100, #collector pipeline
}
DEPTH_LIMIT = 2 # only go 2 links deep, can be configured
DOWNLOAD_DELAY = 0.5 # delay between requests
ROBOTSTXT_OBEY = True
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'