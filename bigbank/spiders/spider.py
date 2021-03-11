import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import BigbankItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class BigbankSpider(scrapy.Spider):
	name = 'bigbank'
	start_urls = ['https://www.bigbank.ee/blogi/']

	def parse(self, response):
		post_links = response.xpath('//a[@class="small"]/@href').getall()
		yield from response.follow_all(post_links, self.parse_category)

	def parse_category(self, response):
		articles = response.xpath('//p[@class="align-left smallest"]/a/@href').getall()
		yield from response.follow_all(articles, self.parse_post)

	def parse_post(self, response):
		date = response.xpath('//p[@class="align-left smallest"]//text()').get().split(' • ')[0]
		title = response.xpath('//h3/text()').get() + 'Subtitle:' + response.xpath('//p[@class="small"]/text()').get()
		content = response.xpath('//ul[@class="bullet-list bullet-mint default color-darkest-gray"]//text() | //div[@class="row wide"]/div[@class="col col-16-24"]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=BigbankItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
