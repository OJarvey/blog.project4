from django.contrib import admin
from .models import Comment, Post, Category


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "post", "created", "active")
    list_filter = ("active", "created", "updated")
    search_fields = ("name", "email", "body")


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "author", "category", "publish", "status")
    list_filter = ("status", "created", "publish", "author", "category")
    search_fields = ("title", "body")
    prepopulated_fields = {"slug": ("title",)}
    raw_id_fields = ("author",)
    date_hierarchy = "publish"
    ordering = ("status", "publish")
    show_facets = admin.ShowFacets.ALWAYS
    fieldsets = (
        (None, {"fields": ("title", "slug", "author", "category", "tags")}),
        ("Content", {"fields": ("body",)}),
        ("Publication", {"fields": ("status", "publish")}),
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
