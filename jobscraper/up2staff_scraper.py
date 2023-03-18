import logging
import sys
import traceback

import requests
from bs4 import BeautifulSoup

from jobscraper.models import Post

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)


def scrape_upstaff():
    try:
        job_links = []
        date_dict = {}
        with open("alljobs.txt", "r") as f:
            for line in f:
                search_query = line.strip()
                url = f"https://up2staff.com/?s={search_query}"
                logger.info(f"Checking URL: {url}")
                response = requests.get(url)
                soup = BeautifulSoup(response.text, "html.parser")

                job_listings = soup.find_all("li", class_="job_listing")
                for listing in job_listings:
                    location = listing.find("div", class_="location").text.strip()
                    date = listing.find("li", class_="date").find("time").text.strip()
                    if "OFF: Anywhere in the World" in location:
                        if "mins" in date or "hours" in date:  # change "days" to "mins"
                            job_link = listing.find("a")["href"]
                            job_links.append(job_link)
                            date_dict[job_link] = date
                            logger.info(f"URL: {job_link} added!")
                    else:
                        logger.info(f"URL not added!")

        job_links = list(set(job_links))
        logger.info(f"Done getting links: ")
        logger.info(f"{job_links}")
        for i in range(len(job_links)):
            link = job_links[i]
            data = requests.get(link)
            soup = BeautifulSoup(data.text, "html.parser")

            title_element = soup.select_one("div.myownheaderforjob h1 a")
            title = title_element.text

            company_element = soup.select_one("div.myownheaderforjob2 div.company")
            job_company_name = company_element.select_one("strong").text

            logo_url = company_element.select_one("img.company_logo")["src"]

            category_element = soup.find(class_="job-type")
            category = category_element.text

            tags_and_content = []
            job_description_text = ""
            description_tags = soup.find_all("div", class_="job_description")
            for tag in description_tags:
                tag_name = tag.name
                tag_content = "\n\n".join(tag.stripped_strings)
                # tag_content = tag.stripped_strings
                #     if ">document.getElementById" in tag_content:
                #         continue
                tags_and_content.append((tag_name, tag_content))
                job_description_text += f"{tag_content} \n\n\n\n"
                job_description = job_description_text.strip()

            application_tag = soup.find("div", class_="application_details")
            a_tag = application_tag.find("a")
            application_link = a_tag.get("href")

            if not Post.objects.filter(
                website_name="up2staff", job_title=title, job_company_name=job_company_name
            ).exists():
                new_post = Post(
                    website_name="up2staff",
                    job_title=title,
                    job_company_name=job_company_name,
                    logo_url=logo_url,
                    job_description=job_description,
                    location=location,
                    category=category,
                    application_link=application_link,
                    post_time=date_dict[link],
                )
                new_post.save()
                logger.info(f"Saved URL: {link} data")
            else:
                # skip creating the new post
                pass
        logger.info(f"Done Scraping")
    except Exception as e:
        logger.error(f"Error occurred at line {sys.exc_info()[-1].tb_lineno}: {str(e)}")
        logger.error(f"Error type: {type(e)}, Error message: {str(e)}")
    return "done"


# scrape_upstaff()


"""
Requests - Requests is a Python library used to send HTTP requests and handle responses. It can be used to fetch data from a website, login to a website, or submit data to a website.

BeautifulSoup - BeautifulSoup is a Python library used to parse HTML and XML documents. It can be used to extract data from web pages, such as titles, links, and images.

Scrapy - Scrapy is a Python framework used for web scraping. It provides a range of tools to extract data from websites, such as automatic crawling, data extraction, and data storage.

PyAutoGUI - PyAutoGUI is a Python library used for automating GUI tasks, such as clicking buttons and typing text. It can be used to simulate user interactions with websites.

Requests-HTML - Requests-HTML is a Python library built on top of the Requests library. It provides additional features, such as HTML parsing and JavaScript rendering, making it easier to scrape dynamic websites.
"""
