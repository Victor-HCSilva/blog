from django.urls import path
from . import admin_panel_views as views

app_name = "admin_panel"

urlpatterns = [
    # Dashboard
    path("", views.dashboard, name="dashboard"),

    # Posts
    path("posts/", views.post_list, name="post_list"),
    path("posts/<int:pk>/", views.post_detail, name="post_detail"),
    path("posts/<int:pk>/edit/", views.post_edit, name="post_edit"),
    path("posts/<int:pk>/publish/", views.post_publish, name="post_publish"),
    path("posts/<int:pk>/unpublish/", views.post_unpublish, name="post_unpublish"),
    path("posts/<int:pk>/delete/", views.post_delete, name="post_delete"),

    # Comentários
    path("comments/", views.comment_list, name="comment_list"),
    path("comments/<int:pk>/", views.comment_detail, name="comment_detail"),
    path("comments/<int:pk>/delete/", views.comment_delete, name="comment_delete"),

    # Usuários
    path("users/", views.user_list, name="user_list"),
    path("users/<int:pk>/", views.user_detail, name="user_detail"),
    path("users/<int:pk>/toggle-status/", views.user_toggle_status, name="user_toggle_status"),
]
