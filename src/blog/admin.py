from django.contrib import admin
from .models import Post, Like, PostView, Comment, Tag


class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'status', 'publish_date']
    search_fields = ['title', 'content']
    list_filter = ['status', 'category', 'publish_date']
    filter_horizontal = ['tags']


admin.site.register(Post, PostAdmin)
admin.site.register(Like)
admin.site.register(PostView)
admin.site.register(Comment)
admin.site.register(Tag)

# Register your models here.
