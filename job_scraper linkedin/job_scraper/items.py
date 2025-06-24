# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class LinkedInJobItem(scrapy.Item):
    job_title = scrapy.Field()
    job_details_url = scrapy.Field()
    job_listed = scrapy.Field()

    company_name = scrapy.Field()
    company_link = scrapy.Field()
    company_location = scrapy.Field()
