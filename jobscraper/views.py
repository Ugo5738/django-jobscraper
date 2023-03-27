import logging
import threading
from datetime import datetime

from django.http import HttpResponse, JsonResponse
from django.utils.timezone import now, timedelta

# from django.shortcuts import render
from django.views.generic import View

from jobscraper.models import Post
from jobscraper.remote_co_scraper import scrape_remote_co
from jobscraper.remote_io_scraper import scrape_remote_io
from jobscraper.up2staff_scraper import scrape_upstaff

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)


class Scrape(View):
    def get(self, request, *args, **kwargs):
        # Configure logging
        # logger = logging.getLogger(__name__)
        # logger.setLevel(logging.INFO)
        # formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        # ch = logging.StreamHandler()
        # ch.setFormatter(formatter)
        # logger.addHandler(ch)

        # Calculate the date for yesterday
        yesterday = now().date() - timedelta(days=1)

        # Filter the posts with fill_date equal to yesterday or earlier
        posts_to_delete = Post.objects.filter(fill_date__lte=yesterday)

        # Delete the posts
        num_deleted, _ = posts_to_delete.delete()
        logger.info(f"Deleted {num_deleted} posts from yesterday backwards.")

        website_name = kwargs["websitename"]
        if website_name == "remoteio":
            logger.info("Starting scraping Remote.io")
            t = threading.Thread(target=scrape_remote_io)
            t.start()
        elif website_name == "remoteco":
            logger.info("Starting scraping Remote.co")
            t = threading.Thread(target=scrape_remote_co)
            t.start()
        elif website_name == "up2staff":
            logger.info("Started scraping Up2Staff")
            t = threading.Thread(target=scrape_upstaff)
            t.start()
        return HttpResponse("Scraping started in the background")


class GetScraped(View):
    def get(self, request, *args, **kwargs):
        website_name = kwargs["websitename"]

        now = datetime.now()
        date = now.strftime("%Y-%m-%d")

        post_list = []
        posts = Post.objects.filter(fill_date=date, website_name=website_name)

        for post in posts:
            if post.job_tags.exists():
                tags = post.job_tags.all()
                post_dict = {
                    "website_name": post.website_name,
                    "job_title": post.job_title,
                    "job_company_name": post.job_company_name,
                    "logo_url": post.logo_url,
                    "job_description": post.job_description,
                    "location": post.location,
                    "category": post.category,
                    "salary_range": post.salary_range,
                    "post_time": post.post_time,
                    "fill_date": post.fill_date,
                    "application_link": post.application_link,
                    "job_tags": [tag.tag_name for tag in tags],
                }
                logger.info(f"Called post with tags")
            else:
                post_dict = {
                    "website_name": post.website_name,
                    "job_title": post.job_title,
                    "job_company_name": post.job_company_name,
                    "logo_url": post.logo_url,
                    "job_description": post.job_description,
                    "location": post.location,
                    "category": post.category,
                    "salary_range": post.salary_range,
                    "post_time": post.post_time,
                    "application_link": post.application_link,
                    "fill_date": post.fill_date,
                }
                logger.info(f"Called post without tags")
            post_list.append(post_dict)
            logger.info(f"Post added to list!")
        logger.info("Done getting posts!")
        if not post_list:
            return HttpResponse("There is scraped data from this api at this time")

        return JsonResponse(post_list, safe=False)
