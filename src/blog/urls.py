from django.urls import path
from .views import post_list, post_create, post_detail, post_update, post_delete, like, about
from .feeds import LatestPostsFeed


app_name = "blog"
urlpatterns = [
    path("", post_list, name="list"),
    path("feed/", LatestPostsFeed(), name="feed"),
    path("about/", about, name="about"),
    path("create/", post_create, name="create"),
    path("<str:slug>/", post_detail, name="detail"),
    path("<str:slug>/update/", post_update, name="update"),
    path("<str:slug>/delete/", post_delete, name="delete"),
    path("<str:slug>/like/", like, name="like"),
]
