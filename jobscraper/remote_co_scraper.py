import logging
import sys

import requests
from bs4 import BeautifulSoup

from jobscraper.models import JobTag, Post

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)


def scrape_remote_co():
    try:
        search_queries = [
            "/remote-jobs/writing/",
            "/remote-jobs/sales/",
            "/remote-jobs/healthcare/",
            "/remote-jobs/project-manager/",
            "/remote-jobs/design/",
            "/remote-jobs/virtual-assistant/",
            "/remote-jobs/developer/",
            "/remote-jobs/it/",
            "/remote-jobs/other/",
            "/remote-jobs/customer-service/",
            "/remote-jobs/recruiter/",
            "/remote-jobs/accounting/",
            "/remote-jobs/online-editing/",
            "/remote-jobs/legal/",
            "/remote-jobs/online-data-entry/",
            "/remote-jobs/qa/",
        ]

        WEB_URL = "https://remote.co"
        job_links = []

        for search_query in search_queries:
            url = f"{WEB_URL}{search_query}"
            response = requests.get(url)
            soup = BeautifulSoup(response.text, "html.parser")

            jobs = soup.find_all("a", {"class": "card"})
            for job in jobs:
                tags = job.find_all("span", {"class": "badge"})
                if any("International" in tag.text for tag in tags):
                    date_str = job.find("date").text
                    if "hours" in date_str or "mins" in date_str:
                        link = job["href"]
                        link = WEB_URL + link
                        job_links.append(link)
                    elif "days" in date_str:
                        continue

        logger.info(job_links)
        for i in range(len(job_links)):
            link = job_links[i]
            data = requests.get(link)
            soup = BeautifulSoup(data.text, "html.parser")

            title = soup.find("h1", class_="font-weight-bold").text

            job_company_name = soup.find("div", class_="co_name").text

            location = soup.find("div", class_="location_sm").text.strip()

            try:
                salary = soup.find("div", class_="salary_sm").text
                salary = salary.split(": ")[1]
            except:
                logger.info(f"No salary: {link}")

            posted_date = soup.find("time")["datetime"]
            posted_time = soup.find("time").text.strip()
            posted_time = posted_time.split(": ")[1]

            job_tags = soup.find_all("a", class_="job_flag")
            job_tags_list = [tag.text for tag in job_tags]

            logo_url = soup.find("img", class_="job_company_logo")["data-lazy-src"]

            job_description_tags = soup.find("div", class_="job_description")
            tags_and_content = []
            job_description_tags = soup.find("div", class_="job_description")
            for tag in job_description_tags.children:
                if tag.name == "h3":
                    p_text = f"{tag.text}\n\n"
                    tags_and_content.append(p_text)
                elif tag.name == "ul":
                    for li in tag.find_all("li"):
                        list_text = f"- {li.text}\n"
                        tags_and_content.append(list_text)
                    tags_and_content.append(f"\n")

                # if tag.name == "strong":
                #     print(tag.text)

                elif tag.name == "p":
                    h3_text = f"{tag.text}\n\n"
                    tags_and_content.append(h3_text)
            job_description = "".join(tags_and_content)

            application_div = soup.find("div", class_="application")
            application_link = application_div.find("a")["href"]

            if not Post.objects.filter(
                website_name="remoteco", job_title=title, job_company_name=job_company_name
            ).exists():
                new_post = Post(
                    website_name="remoteco",
                    job_title=title,
                    job_company_name=job_company_name,
                    logo_url=logo_url,
                    job_description=job_description,
                    location=location,
                    category=" ".join(job_tags_list),
                    application_link=application_link,
                    post_time=posted_time,
                )
                new_post.save()
                logger.info(f"Saved URL: {link} data")

                # Create JobTag instances and associate them with the newly created Post
                for tag_text in job_tags_list:
                    job_tag = JobTag(tag_name=tag_text, post=new_post)
                    job_tag.save()
            else:
                # skip creating the new post
                pass
        logger.info(f"Done Scraping")
    except Exception as e:
        logger.error(f"Error occurred at line {sys.exc_info()[-1].tb_lineno}: {str(e)}")
        logger.error(f"Error type: {type(e)}, Error message: {str(e)}")
    return "done"
