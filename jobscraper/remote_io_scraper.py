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


def scrape_remote_io():
    try:
        search_queries = [
            "/remote-software-development-jobs",
            "/remote-data-jobs",
            "/remote-design-jobs",
            "/remote-product-jobs",
            "/remote-business-development-jobs",
        ]

        WEB_URL = "https://www.remote.io"
        job_links = []

        for search_query in search_queries:
            url = f"{WEB_URL}{search_query}"

            response = requests.get(url)
            soup = BeautifulSoup(response.content, "html.parser")

            cards = soup.find_all(
                "div",
                class_="lg:flex shadow-singlePost hover:bg-gray-600 items-center hidden px-5 py-3 space-x-6 bg-white rounded-md cursor-pointer relative",
            )

            for card in cards:
                # job_title = card.find("a", class_="font-500 text-lg text-black whitespace-pre-wrap").text.strip()
                # company_name = card.find("p", class_="font-400 mb-1 text-gray-300").text.strip()
                time_posted = card.find("span", class_="text-gray-400").text
                job_location = card.find(
                    "a",
                    class_="px-2 py-1 text-xs uppercase inline-flex items-center font-500 md:rounded-sm rounded-xs whitespace-pre-line bg-opacity-10 bg-black text-gray-300",
                )
                if job_location is not None:
                    location = job_location.text.strip()
                else:
                    continue

                if "anywhere" not in location.lower():
                    if "h" in time_posted or "m" in time_posted:
                        card_link = card.find(
                            "a", class_="font-500 text-lg text-black whitespace-pre-wrap"
                        ).get("href")
                        link = WEB_URL + card_link
                        job_links.append(link)

        logger.info(job_links)
        for i in range(len(job_links)):
            link = job_links[i]
            response = requests.get(link)
            soup = BeautifulSoup(response.content, "html.parser")

            title = soup.find("h1", {"class": "styles_title__3gFK4"}).text.strip()

            job_company_name = soup.find("p", {"data-rewrite": "job-company-name"}).text

            logo_element = soup.find("div", {"class": "styles_logo__1_efV"})
            logo_url = logo_element.find("img")["src"]

            tag_elements = soup.find_all("a", {"data-tag": "true"})
            job_tags_list = [tag.text for tag in tag_elements]

            job_description = soup.find("div", {"id": "job-description"}).text

            application_element = soup.find(
                "div", {"class": "md:hidden bottom-2 md:space-y-6 sticky block col-span-12 mt-6 space-y-4"}
            )
            application_url = application_element.find("a")["href"]
            application_link = f"{WEB_URL}{application_url}"

            category = soup.find(
                "a",
                {
                    "class": "border-transparent px-1 text-xs uppercase border-2 border-solid text-white font-500 bg-gray-300 rounded-sm flex-shrink-0 mr-1 mb-1 items-center"
                },
            ).text

            location_salary_elements = soup.find_all("div", {"class": "text-base text-gray-100"})
            location = location_salary_elements[0].text.strip()
            try:
                salary = location_salary_elements[1].text.strip()
            except:
                logger.info("There is no salary for this job!")

            card_element = soup.find("ul", {"class": "top-0 p-4 space-y-4 bg-gray-600 rounded-md"})
            li_tags = card_element.find_all("li")
            _, num, day, text = li_tags[-1].text.strip().split()
            posted_time = f"{num} {day} {text}"

            if not Post.objects.filter(
                website_name="remoteio", job_title=title, job_company_name=job_company_name
            ).exists():
                if salary:
                    new_post = Post(
                        website_name="remoteio",
                        job_title=title,
                        job_company_name=job_company_name,
                        salary_range=salary,
                        logo_url=logo_url,
                        job_description=job_description,
                        location=location,
                        category=category,
                        application_link=application_link,
                        post_time=posted_time,
                    )
                else:
                    new_post = Post(
                        website_name="remoteio",
                        job_title=title,
                        job_company_name=job_company_name,
                        logo_url=logo_url,
                        job_description=job_description,
                        location=location,
                        category=category,
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
