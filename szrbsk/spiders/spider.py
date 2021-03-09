import re

import scrapy

from scrapy.loader import ItemLoader
from w3lib.html import remove_tags

from ..items import SzrbskItem
from itemloaders.processors import TakeFirst


class SzrbskSpider(scrapy.Spider):
	name = 'szrbsk'
	start_urls = ['https://www.szrb.sk/sk/novinky/']

	def parse(self, response):
		post_links = response.xpath('//div[@class="wm_news_box"]//h2/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = response.xpath('//a[@title="Archív"]/@href').getall()
		yield from response.follow_all(next_page, self.parse)

	def parse_post(self, response):
		title = response.xpath('//h1//text()').get()
		description = response.xpath('//div[@class="wm_news_box"]//text()[normalize-space() and not(ancestor::h1 | ancestor::div[@class="time"] | ancestor::a)]').getall()
		description = [remove_tags(p).strip() for p in description]
		description = ' '.join(description).strip()
		date = response.xpath('//div[@class="wm_news_box"]/div[@class="time"]/text()').get()
		if date:
			date = re.findall(r'\d+\.\d+\.\d+', date)

		item = ItemLoader(item=SzrbskItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
