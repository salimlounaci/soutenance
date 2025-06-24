import re

from itemloaders.processors import MapCompose, TakeFirst
from scrapy.loader import ItemLoader


def extract_relatice_time(text):
    match = re.search(r'\b\d+\s+(seconds?|minutes?|hours?|days?|weeks?|months?|years?)\s+ago\b', text)
    return match.group() if match else None

def clean_text(text):
    return text.strip() if text else None

def split_location(text):
    parts = [part.strip for part in text.split(',')]
    if len(parts) == 3:
        return parts
    return [None, None, None]

class LinkedInJobItemLoader(ItemLoader):

    default_output_processor = TakeFirst()
    job_listed_in = MapCompose(str.strip, extract_relatice_time)
    company_location_in = MapCompose(str.strip, clean_text)
    company_name_in = MapCompose(str.strip, clean_text)
    job_title_in = MapCompose(str.strip, clean_text)


