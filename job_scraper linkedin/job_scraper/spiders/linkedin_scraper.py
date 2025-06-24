from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

import scrapy
from job_scraper.items import LinkedInJobItem
from job_scraper.itemsloaders import LinkedInJobItemLoader


def update_start_param(url, new_start):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    query_params["start"] = [str(new_start)]
    new_query = urlencode(query_params, doseq=True)
    new_url = urlunparse(parsed_url._replace(query=new_query))
    return new_url


class LinkedinScraperSpider(scrapy.Spider):
    name = "linkedin_scraper"
    start_urls = [
        "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?&location=France&start="
    ]

    async def start(self):
        first_job_on_page = 0
        first_url = update_start_param(self.start_urls[0], first_job_on_page)
        yield scrapy.Request(
            url=first_url,
            callback=self.parse_job,
            meta={'first_job_on_page': first_job_on_page},
        )


    def parse_job(self, response):
        first_job_on_page = response.meta["first_job_on_page"]

        jobs = response.css("li")

        number_of_jobs = len(jobs)

        for job in jobs:
            job_item = LinkedInJobItemLoader(item=LinkedInJobItem(), selector=job)
            job_item.add_css("job_title", "h3::text")
            job_item.add_css("job_details_url", ".base-card__full-link::attr(href)")
            job_item.add_css("job_listed", "time::text")

            job_item.add_css("company_name", "h4 a::text")
            job_item.add_css("company_link", "h4 a::attr(href)")
            job_item.add_css("company_location", ".job-search-card__location::text")
            yield job_item.load_item()

        if number_of_jobs > 0:
            first_job_on_page = int(first_job_on_page) + 25
            next_url = update_start_param(response.url, first_job_on_page)
            yield scrapy.Request(
                url=next_url,
                callback=self.parse_job,
                meta={'first_job_on_page': first_job_on_page},
            )
