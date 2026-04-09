from django.contrib import admin
from .models import Post, Like, PostView, Comment, Tag, NewsletterSubscriber


class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'status', 'publish_date']
    search_fields = ['title', 'content']
    list_filter = ['status', 'category', 'publish_date']
    filter_horizontal = ['tags']


class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ['email', 'is_active', 'created_at']
    search_fields = ['email']
    list_filter = ['is_active', 'created_at']


admin.site.register(Post, PostAdmin)
admin.site.register(Like)
admin.site.register(PostView)
admin.site.register(Comment)
admin.site.register(Tag)
admin.site.register(NewsletterSubscriber, NewsletterSubscriberAdmin)

# Register your models here.
