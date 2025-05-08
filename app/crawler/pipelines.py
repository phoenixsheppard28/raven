class ResultCollectorPipeline:
    """
    Pipeline that collects all scraped items in a list,
    """
    def __init__(self):
        self.items = []
    
    def process_item(self, item, spider):
        self.items.append(item)
        return item
        
    def close_spider(self, spider):
        spider.collected_items = self.items
    