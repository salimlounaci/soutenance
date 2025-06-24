# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


import os

# useful for handling different item types with a single interface
import mysql.connector
from dotenv import load_dotenv

load_dotenv()


class MySQLNoDucplicatesPipeline:
    def __init__(self):
        self.connection = mysql.connector.connect(
            host=os.environ.get("DB_HOST"),
            user=os.environ.get("DB_USER"),
            password=os.environ.get("DB_PASSWORD"),
            database=os.environ.get("DB_NAME"),
            port=os.environ.get("DB_PORT", 3306),
        )
        self.cursor = self.connection.cursor()

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            job_title VARCHAR(255) NOT NULL,
            job_details_url VARCHAR(255) NOT NULL UNIQUE,
            job_listed VARCHAR(255),
            company_name VARCHAR(255),
            company_link VARCHAR(255),
            city VARCHAR(255),
            department VARCHAR(255),
            country VARCHAR(255)
        )
        """)

    def process_item(self, item, spider):
        self.cursor.execute(
            "SELECT * FROM jobs WHERE job_details_url = %s", (item["job_details_url"],)
        )
        result = self.cursor.fetchone()

        if result:
            spider.logger.info(
                f"Job already exists in Database: {item['job_details_url']}"
            )
        else:
            city, department, country = (
                item["company_location"].split(", ")
                if item["company_location"]
                else (None, None, None)
            )
            self.cursor.execute(
                """
            INSERT INTO jobs (job_title, job_details_url, job_listed, company_name, company_link, city, department, country)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
                (
                    item["job_title"],
                    item["job_details_url"],
                    item["job_listed"],
                    item["company_name"],
                    item["company_link"],
                    city,
                    department,
                    country,
                ),
            )
        self.connection.commit()
        return item

    def close_spider(self, spider):
        self.cursor.close()
        self.connection.close()
        spider.logger.info("MySQL connection closed.")