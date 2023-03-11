import logging
import os
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from jobscraper.models import Post

# Configure logging
# logging.basicConfig(filename='example.log', level=logging.ERROR)
logging.basicConfig(level=logging.ERROR)


def scrape_upstaff():
    try:
        jobs_dict = {}
        job_list = []
        date_dict = {}
        job_links = []
        one_job_dict = {}
        job_description_text = ""

        BASE_DIR = Path(__file__).resolve().parent.parent
        # DRIVER_PATH = os.path.join(BASE_DIR, "chromedriver.exe")
        DRIVER_PATH = "chromedriver.exe"
        WEB_URL = "https://up2staff.com/"

        options = Options()
        options.add_argument("--headless")
        service = Service(DRIVER_PATH)
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(WEB_URL)

        search_input = driver.find_element(By.ID, "search_keywords")
        search_input.send_keys("Full-stack programming")
        search_input.submit()

        # We don't need to load more pages because we focusing on jobs that were posted that day which might be a lot
        # for i in range(5):
        #     button = driver.find_element(By.ID, "load_more_jobs_myid")
        #     driver.execute_script("arguments[0].scrollIntoView();", button)
        #     button.click()
        #     time.sleep(10)

        wait = WebDriverWait(driver, 30)
        job_listings = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li.job_listing")))

        for job in job_listings:
            # # Extract the job title and company name
            # job_title = job.find_element(By.CLASS_NAME, "position").text
            # company_name = job.find_element(By.CLASS_NAME, "company").text

            # # Extract the job type and location
            # job_type = job.find_element(By.CLASS_NAME, "job-type").text
            location = job.find_element(By.CLASS_NAME, "location").text
            date = job.find_element(By.CLASS_NAME, "date").text.split()

            if "OFF: Anywhere in the World" in location:
                if "hours" in date or "mins" in date:
                    job_link = job.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
                    job_links.append(job_link)
                    date_dict[job_link] = date[0] + " " + date[1] + " " + date[2]

        job_links = list(set(job_links))

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
            description_tags = soup.find_all("div", class_="job_description")
            for tag in description_tags:
                tag_name = tag.name
                tag_content = "\n\n".join(tag.stripped_strings)
                # tag_content = tag.stripped_strings
                #     if ">document.getElementById" in tag_content:
                #         continue
                tags_and_content.append((tag_name, tag_content))
                job_description_text += f"{tag_content} \n\n\n\n"

            jobs_dict[title] = job_description_text

            if not Post.objects.filter(
                website_name="Up2staff", job_title=title, job_company_name=job_company_name
            ).exists():
                # create a new post
                new_post = Post(
                    website_name="Up2staff",
                    job_title=title,
                    job_company_name=job_company_name,
                    logo_url=logo_url,
                    job_description=job_description_text,
                    location=location,
                    category=category,
                    post_time=date_dict[link],
                )

                new_post.save()
            else:
                # skip creating the new post
                pass

            one_job_dict["Title"] = title
            one_job_dict["Job Company Name"] = job_company_name
            # one_job_dict["Job Tags"] = job_tags
            one_job_dict["Logo"] = logo_url
            one_job_dict["Job Description"] = job_description_text
            one_job_dict["Location"] = location
            one_job_dict["Category"] = category
            # one_job_dict["Salary Range"] = salary_range
            one_job_dict["Posted Date"] = date_dict[link]

            job_list.append(one_job_dict)

            # Click on the next link, unless this is the last link in the list
            if i < len(job_links) - 1:
                next_link = job_links[i + 1]
                driver.get(next_link)
                time.sleep(2)  # Add a delay to allow the page to load

        time.sleep(5)
        driver.quit()
    except Exception as e:
        logging.error(str(e))
    return "done"

    # return job_list


# scrape_upstaff()
