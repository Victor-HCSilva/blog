from django.contrib import admin
from .models import Comment, Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "is_published", "created_at", "updated_at")
    list_filter = ("is_published", "created_at", "author")
    search_fields = ("title", "content", "author__username")
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "created_at"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("post", "author", "is_active", "created_at")
    list_filter = ("is_active", "created_at", "author")
    search_fields = ("content", "author__username", "post__title")
