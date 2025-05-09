BOT_NAME = 'crawler'
SPIDER_MODULES = ['app.crawler.spiders']
NEWSPIDER_MODULE = 'app.crawler.spiders'
ITEM_PIPELINES = {
    'app.crawler.pipelines.ResultCollectorPipeline': 100, #collector pipeline
}
DEPTH_LIMIT = 2 # only go 2 links deep, can be configured
DOWNLOAD_DELAY = 0.5 # delay between requests
ROBOTSTXT_OBEY = True
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
IGNORED_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.css', '.js']
GPT_MODEL = "gpt-4.1-nano"
GPT_MAX_TOKENS = 17
DEFAULT_TARGET_KEYWORDS = [
    "Budget", "ACFR", "Finance Director", "CFO", "Financial Report",
    "Expenditure", "Revenue", "General Fund", "Capital Improvement Plan",
    "Fiscal Year", "Audit", "Auditor", "Treasurer", "Bond Issuance",
    "Municipal Bonds", "Debt Service", "Fund Balance", "Operating Budget",
    "Financial Statement", "Public Finance", "Controller", "Accounting",
    "CAFR", "GFOA", "Financial Planning", "Budget Hearing", "Budget Proposal",
    "Budget Adoption", "Reserve Fund", "Financial Forecast"
]