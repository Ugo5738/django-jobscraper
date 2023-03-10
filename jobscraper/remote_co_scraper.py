import os
import time
from pathlib import Path

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from jobscraper.models import JobTag, Post


def scrape_remote_co():
    job_dict = {}
    jobs_dict = {}
    job_links = []
    job_description_text = ""

    BASE_DIR = Path(__file__).resolve().parent.parent
    DRIVER_PATH = os.path.join(BASE_DIR, "chromedriver.exe")
    WEB_URL = "https://remote.co"

    options = Options()
    # options.add_argument("--headless")
    service = Service(DRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)

    start_timer = time.monotonic()
    driver.get(WEB_URL)
    end_timer = time.monotonic()
    elapsed_time = end_timer - start_timer
    print(f"Elapsed time for page load 1: {elapsed_time/60:.2f} minutes")

    start_timer = time.monotonic()
    developer_link = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//a[contains(@href,'/remote-jobs/developer/')]"))
    )
    developer_link.click()
    end_timer = time.monotonic()
    elapsed_time = end_timer - start_timer
    print(f"Elapsed time for page load 2: {elapsed_time/60:.2f} minutes")

    html = driver.page_source

    # Parse HTML using BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")
    jobs = soup.find_all("a", {"class": "card"})

    for job in jobs:
        tags = job.find_all("span", {"class": "badge"})
        if any("International" in tag.text for tag in tags):
            date_str = job.find("date").text
            # include minutes in this logic
            if "hours" in date_str:
                link = job["href"]
                link = WEB_URL + link
                job_links.append(link)
            elif "days" in date_str:
                print("there is days in this job card")

    for i in range(len(job_links)):
        link = job_links[i]
        driver.get(link)

        title = driver.find_element(By.CLASS_NAME, "font-weight-bold").text
        job_company_name = driver.find_element(By.XPATH, "//h1[contains(text(),'at')]").text.split("at ")[1]
        job_tags = [tag.text for tag in driver.find_elements(By.CLASS_NAME, "job_flag")]
        logo_url = driver.find_element(By.CLASS_NAME, "job_company_logo").get_attribute("src")
        print("Logo Url: ", logo_url)
        if "data:image" in logo_url:
            driver.quit()
            scrape_remote_co()

        job_description = driver.find_element(By.CLASS_NAME, "job_description")
        elements = job_description.find_elements(By.XPATH, ".//*")
        job_description_dict = {}
        for element in elements:
            text = element.text.strip()
            if text:
                job_description_dict[element.tag_name] = text  # solve the issue of not having duplicate keys
                job_description_text += f"{text} \n\n"
        posted_time = driver.find_element(By.XPATH, "//time").text.split("Posted: ")[1]
        location = (
            driver.find_element(By.CLASS_NAME, "location_sm")
            .find_element(By.CLASS_NAME, "col-10")
            .text.split(": ")[1]
        )
        if not Post.objects.filter(
            website_name="Up2staff", job_title=title, job_company_name=job_company_name
        ).exists():
            new_post = Post(
                website_name="Remote CO",
                job_title=title,
                job_company_name=job_company_name,
                # job_tags=job_tags,
                logo_url=logo_url,
                job_description=job_description_text,
                location=location,
                # category=category,
                # salary_range=salary_range,
                post_time=posted_time,
            )

            new_post.save()

            for job_tag in job_tags:
                tag = JobTag(tag_name=job_tag)
                tag.post = new_post
                tag.save()
        else:
            # skip creating the new post
            pass

        #     one_job_dict = {}
        #     one_job_dict["Job Title"] = title
        #     one_job_dict["Job Company Name"] = job_company_name
        #     one_job_dict["Job Tags"] = job_tags
        #     one_job_dict["Logo"] = logo_url
        #     one_job_dict["Job Description"] = job_description
        #     one_job_dict["Location"] = location
        #     # one_job_dict["Category"] = category
        #     # one_job_dict["Salary Range"] = salary_range
        #     one_job_dict["Posted Date"] = posted_time

        #     jobs_dict[f"job_{i+1}"] = one_job_dict

        # Click on the next link, unless this is the last link in the list
        if i < len(job_links) - 1:
            next_link = job_links[i + 1]
            driver.get(next_link)
            time.sleep(2)  # Add a delay to allow the page to load

    driver.quit()
    return "done"
    # return jobs_dict


# scrape_remote_co()
