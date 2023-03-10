from django.db import models
from django.utils.timezone import now


class Post(models.Model):
    website_name = models.CharField(max_length=100)
    job_title = models.CharField(max_length=100)
    job_company_name = models.CharField(max_length=100)
    logo_url = models.CharField(max_length=100)
    job_description = models.CharField(max_length=20000)
    location = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    salary_range = models.CharField(max_length=100)
    post_time = models.CharField(max_length=100)
    fill_date = models.CharField(max_length=100, default=now().strftime("%Y-%m-%d"))

    def __str__(self):
        return f"{self.website_name}"


class JobTag(models.Model):
    tag_name = models.CharField(max_length=100)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="job_tags")

    def __str__(self):
        return f"{self.tag_name}>"
