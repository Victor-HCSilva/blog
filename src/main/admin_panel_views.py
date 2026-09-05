from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .admin_panel_auth import admin_required
from .admin_panel_forms import AdminPostForm
from .models import Comment, Post


@admin_required
def dashboard(request):
    """
    Dashboard administrativo com indicadores do sistema:
    - Total de posts
    - Posts publicados
    - Posts em rascunho
    - Total de comentários
    - Total de usuários
    """
    total_posts = Post.objects.count()
    published_posts = Post.objects.filter(is_published=True).count()
    draft_posts = Post.objects.filter(is_published=False).count()
    total_comments = Comment.objects.count()
    total_users = User.objects.count()

    recent_posts = (
        Post.objects.select_related("author")
        .annotate(comments_count=Count("comments"))
        .order_by("-created_at")[:5]
    )
    recent_comments = (
        Comment.objects.select_related("author", "post")
        .order_by("-created_at")[:5]
    )

    context = {
        "total_posts": total_posts,
        "published_posts": published_posts,
        "draft_posts": draft_posts,
        "total_comments": total_comments,
        "total_users": total_users,
        "recent_posts": recent_posts,
        "recent_comments": recent_comments,
    }
    return render(request, "admin_panel/dashboard.html", context)


# ==========================================
# GERENCIAMENTO DE POSTS
# ==========================================

@admin_required
def post_list(request):
    """
    Listagem de posts com filtros por status de publicação e por autor.
    """
    status = request.GET.get("status", "").strip().lower()
    author_id = request.GET.get("author", "").strip()

    posts = (
        Post.objects.select_related("author")
        .annotate(comments_count=Count("comments"))
        .order_by("-created_at")
    )

    if status == "published":
        posts = posts.filter(is_published=True)
    elif status == "draft":
        posts = posts.filter(is_published=False)

    if author_id.isdigit():
        posts = posts.filter(author_id=int(author_id))

    authors = User.objects.filter(posts__isnull=False).distinct().order_by("username")

    context = {
        "posts": posts,
        "authors": authors,
        "selected_status": status,
        "selected_author": int(author_id) if author_id.isdigit() else None,
    }
    return render(request, "admin_panel/posts/list.html", context)


@admin_required
def post_detail(request, pk):
    """
    Visualização detalhada de um post dentro do painel administrativo.
    """
    post = get_object_or_404(
        Post.objects.select_related("author").annotate(comments_count=Count("comments")),
        pk=pk,
    )
    comments = post.comments.select_related("author").order_by("-created_at")

    context = {
        "post": post,
        "comments": comments,
    }
    return render(request, "admin_panel/posts/detail.html", context)


@admin_required
def post_edit(request, pk):
    """
    Edição administrativa de post existente.
    """
    post = get_object_or_404(Post, pk=pk)

    if request.method == "POST":
        form = AdminPostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, f"Publicação '{post.title}' atualizada com sucesso!")
            return redirect("admin_panel:post_detail", pk=post.pk)
    else:
        form = AdminPostForm(instance=post)

    context = {
        "form": form,
        "post": post,
    }
    return render(request, "admin_panel/posts/form.html", context)


@admin_required
@require_POST
def post_publish(request, pk):
    """
    Publica uma postagem. Exige POST e CSRF.
    """
    post = get_object_or_404(Post, pk=pk)
    post.is_published = True
    post.save()
    messages.success(request, f"Publicação '{post.title}' foi publicada com sucesso!")
    next_url = request.POST.get("next") or reverse("admin_panel:post_list")
    return redirect(next_url)


@admin_required
@require_POST
def post_unpublish(request, pk):
    """
    Despublica uma postagem (move para rascunho). Exige POST e CSRF.
    """
    post = get_object_or_404(Post, pk=pk)
    post.is_published = False
    post.save()
    messages.info(request, f"Publicação '{post.title}' foi despublicada (rascunho).")
    next_url = request.POST.get("next") or reverse("admin_panel:post_list")
    return redirect(next_url)


@admin_required
def post_delete(request, pk):
    """
    Exclusão de postagem. GET exibe tela de confirmação, POST efetua a exclusão.
    """
    post = get_object_or_404(Post, pk=pk)

    if request.method == "POST":
        post_title = post.title
        post.delete()
        messages.success(request, f"Publicação '{post_title}' excluída definitivamente.")
        return redirect("admin_panel:post_list")

    return render(request, "admin_panel/posts/confirm_delete.html", {"post": post})


# ==========================================
# GERENCIAMENTO DE COMENTÁRIOS
# ==========================================

@admin_required
def comment_list(request):
    """
    Listagem de comentários com autor, post relacionado, data e status (is_active).
    """
    status = request.GET.get("status", "").strip().lower()

    comments = (
        Comment.objects.select_related("author", "post")
        .order_by("-created_at")
    )

    if status == "active":
        comments = comments.filter(is_active=True)
    elif status == "inactive":
        comments = comments.filter(is_active=False)

    context = {
        "comments": comments,
        "selected_status": status,
    }
    return render(request, "admin_panel/comments/list.html", context)


@admin_required
def comment_detail(request, pk):
    """
    Visualização detalhada de um comentário.
    """
    comment = get_object_or_404(
        Comment.objects.select_related("author", "post"),
        pk=pk,
    )
    return render(request, "admin_panel/comments/detail.html", {"comment": comment})


@admin_required
def comment_delete(request, pk):
    """
    Exclusão de comentário. GET exibe tela de confirmação, POST exclui via CSRF.
    """
    comment = get_object_or_404(Comment.objects.select_related("post", "author"), pk=pk)

    if request.method == "POST":
        comment.delete()
        messages.success(request, "Comentário excluído com sucesso.")
        return redirect("admin_panel:comment_list")

    return render(request, "admin_panel/comments/confirm_delete.html", {"comment": comment})


# ==========================================
# GERENCIAMENTO DE USUÁRIOS
# ==========================================

@admin_required
def user_list(request):
    """
    Listagem de usuários com status, indicadores de staff/superuser e contadores.
    """
    users = (
        User.objects.annotate(
            posts_count=Count("posts", distinct=True),
            comments_count=Count("comments", distinct=True),
        )
        .order_by("-date_joined")
    )
    return render(request, "admin_panel/users/list.html", {"users": users})


@admin_required
def user_detail(request, pk):
    """
    Visualização de perfil e histórico de atividades de um usuário.
    """
    user_obj = get_object_or_404(
        User.objects.annotate(
            posts_count=Count("posts", distinct=True),
            comments_count=Count("comments", distinct=True),
        ),
        pk=pk,
    )
    user_posts = user_obj.posts.order_by("-created_at")[:10]
    user_comments = user_obj.comments.select_related("post").order_by("-created_at")[:10]

    context = {
        "target_user": user_obj,
        "user_posts": user_posts,
        "user_comments": user_comments,
    }
    return render(request, "admin_panel/users/detail.html", context)


@admin_required
@require_POST
def user_toggle_status(request, pk):
    """
    Ativa ou desativa um usuário com proteção CSRF.
    Impede que o administrador logado desative a si próprio.
    """
    user_obj = get_object_or_404(User, pk=pk)

    if user_obj == request.user:
        messages.error(request, "Operação bloqueada: você não pode desativar a si próprio!")
        return redirect("admin_panel:user_list")

    user_obj.is_active = not user_obj.is_active
    user_obj.save()

    status_label = "ativado" if user_obj.is_active else "desativado"
    messages.success(request, f"Usuário '{user_obj.username}' foi {status_label} com sucesso.")
    next_url = request.POST.get("next") or reverse("admin_panel:user_list")
    return redirect(next_url)
