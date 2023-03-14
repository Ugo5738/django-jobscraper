import threading
from datetime import datetime

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.generic import View

from jobscraper.models import Post
from jobscraper.remote_co_scraper import scrape_remote_co
from jobscraper.remote_io_scraper import scrape_remote_io
from jobscraper.up2staff_scraper import scrape_upstaff


class Scrape(View):
    def get(self, request, *args, **kwargs):
        website_name = kwargs["websitename"]
        if website_name == "remoteio":
            # scrape_remote_io()
            t = threading.Thread(target=scrape_remote_io)
            t.start()
        elif website_name == "remoteco":
            # scrape_remote_co()
            t = threading.Thread(target=scrape_remote_co)
            t.start()
        elif website_name == "up2staff":
            # scrape_upstaff()
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
                    "job_tags": [tag.tag_name for tag in tags],
                }
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
                    "fill_date": post.fill_date,
                }
            post_list.append(post_dict)

        return JsonResponse(post_list, safe=False)
