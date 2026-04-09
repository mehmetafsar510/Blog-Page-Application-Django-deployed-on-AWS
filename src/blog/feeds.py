from django.contrib.syndication.views import Feed
from django.urls import reverse
from .models import Post


class LatestPostsFeed(Feed):
    title = "Clarusway Blog - Latest Posts"
    link = "/blog/"
    description = "Latest posts from Clarusway Blog"

    def items(self):
        return Post.objects.filter(status='p').order_by('-publish_date')[:10]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.content

    def item_link(self, item):
        return reverse('blog:detail', args=[item.slug])

    def item_author_name(self, item):
        return item.author.get_full_name() or item.author.username

    def item_pubdate(self, item):
        return item.publish_date
