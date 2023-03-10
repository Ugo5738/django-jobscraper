from django.contrib import admin

from jobscraper import models

admin.site.register(models.Post)
admin.site.register(models.JobTag)
