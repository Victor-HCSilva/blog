from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

app_name = "main"

urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.CustomLoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="main:home"), name="logout"),
    path("cadastro/", views.create_account, name="create_account"),
    path("create_account/", views.create_account, name="create_account_alias"),
    path("sobre/", views.sobre, name="sobre"),
    # Publicações
    path("posts/novo/", views.post_create, name="post_create"),
    path("meus-posts/", views.user_posts, name="user_posts"),
    path("post/<slug:slug>/", views.post_detail, name="post_detail"),
    path("post/id/<int:pk>/", views.post_detail, name="post_detail_pk"),
    path("post/<int:pk>/editar/", views.post_edit, name="post_edit"),
    path("post/<int:pk>/excluir/", views.post_delete, name="post_delete"),
    # Comentários
    path("post/<int:pk>/comentar/", views.comment_create, name="comment_create"),
    path("comentario/<int:pk>/excluir/", views.comment_delete, name="comment_delete"),
]
