from django.contrib.sitemaps import Sitemap
from django.db import models
from django.utils import timezone
from .models import Post


class PostSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8

    def items(self):
        return Post.objects.filter(status='p').filter(
            models.Q(published_date__lte=timezone.now()) | models.Q(published_date__isnull=True)
        )

    def lastmod(self, obj):
        return obj.get_published_date()

    def location(self, obj):
        return obj.get_absolute_url()
