from django.urls import path

from jobscraper import views

urlpatterns = [
    path("scrape/<websitename>", views.Scrape.as_view(), name="scrape"),
    path("get-scrape/<websitename>", views.GetScraped.as_view(), name="get_scrape"),
]
