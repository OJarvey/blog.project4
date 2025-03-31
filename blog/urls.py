from django.urls import path
from . import views
from .feeds import LatestPostsFeed

app_name = "blog"

urlpatterns = [
    path("", views.post_list_with_categories, name="post_list"),
    path("tag/<slug:tag_slug>/", views.post_list_with_categories, name="post_list_by_tag"),
    path("<int:year>/<int:month>/<int:day>/<slug:post>/", views.post_detail, name="post_detail"),
    path("<int:post_id>/share/", views.post_share, name="post_share"),
    path("<int:post_id>/comment/", views.post_comment, name="post_comment"),
    path("comment/<int:comment_id>/toggle/", views.toggle_comment_status, name="toggle_comment_status"),
    path("feed/", LatestPostsFeed(), name="post_feed"),
    path("search/", views.post_search, name="post_search"),
    path("create/", views.post_create, name="post_create"),
    path("<int:post_id>/edit/", views.post_update, name="post_update"),
    path("<int:post_id>/delete/", views.post_delete, name="post_delete"),
    path("category/<slug:category_slug>/", views.post_list_by_category, name="post_list_by_category"),
    path("<int:post_id>/like/", views.post_like, name="post_like"),
]