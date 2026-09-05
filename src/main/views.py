from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST

from .forms import CommentForm, PostForm, UserForm
from .models import Comment, Post


def home(request):
    """Feed principal: lista postagens públicas ordenadas cronologicamente."""
    query = request.GET.get("q", "").strip()
    posts = Post.objects.filter(is_published=True).select_related("author").prefetch_related("comments")

    if query:
        posts = posts.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        )

    return render(request, "blog/home.html", {"posts": posts, "query": query})


def post_detail(request, slug=None, pk=None):
    """Exibe os detalhes de uma publicação e seus comentários."""
    if slug:
        post = get_object_or_404(Post, slug=slug)
    else:
        post = get_object_or_404(Post, pk=pk)

    # Proteção de rascunhos: apenas o autor pode ver
    if not post.is_published and post.author != request.user:
        raise Http404("Publicação não encontrada ou indisponível.")

    comments = post.comments.filter(is_active=True).select_related("author")
    comment_form = CommentForm()

    return render(
        request,
        "blog/post_detail.html",
        {
            "post": post,
            "comments": comments,
            "comment_form": comment_form,
        },
    )


@login_required
def post_create(request):
    """Criação de uma nova publicação pelo usuário autenticado."""
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, "Publicação criada com sucesso!")
            return redirect(post.get_absolute_url())
    else:
        form = PostForm()

    return render(request, "blog/post_form.html", {"form": form, "action": "Criar Publicação"})


@login_required
def post_edit(request, pk):
    """Edição de publicação existente. Apenas o autor tem permissão."""
    post = get_object_or_404(Post, pk=pk)

    if post.author != request.user:
        raise PermissionDenied("Você não tem permissão para editar esta publicação.")

    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, "Publicação atualizada com sucesso!")
            return redirect(post.get_absolute_url())
    else:
        form = PostForm(instance=post)

    return render(
        request,
        "blog/post_form.html",
        {"form": form, "post": post, "action": "Editar Publicação"},
    )


@login_required
def post_delete(request, pk):
    """Exclusão de publicação. Apenas o autor tem permissão."""
    post = get_object_or_404(Post, pk=pk)

    if post.author != request.user:
        raise PermissionDenied("Você não tem permissão para excluir esta publicação.")

    if request.method == "POST":
        post.delete()
        messages.success(request, "Publicação excluída com sucesso!")
        return redirect("main:user_posts")

    return render(request, "blog/post_confirm_delete.html", {"post": post})


@login_required
def user_posts(request):
    """Painel do autor: lista todas as publicações do usuário (publicadas e rascunhos)."""
    posts = Post.objects.filter(author=request.user).order_by("-created_at")
    return render(request, "blog/user_posts.html", {"posts": posts})


@login_required
@require_POST
def comment_create(request, pk):
    """Cria um comentário associado a um post."""
    post = get_object_or_404(Post, pk=pk)

    if not post.is_published and post.author != request.user:
        raise Http404("Publicação indisponível.")

    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
        messages.success(request, "Comentário adicionado com sucesso!")
    else:
        messages.error(request, "Não foi possível enviar seu comentário. Verifique os dados.")

    return redirect(post.get_absolute_url())


@login_required
@require_POST
def comment_delete(request, pk):
    """Exclui um comentário. Apenas o autor do comentário ou o autor do post podem excluir."""
    comment = get_object_or_404(Comment, pk=pk)
    post = comment.post

    if comment.author != request.user and post.author != request.user:
        raise PermissionDenied("Você não tem permissão para excluir este comentário.")

    comment.delete()
    messages.success(request, "Comentário removido.")
    return redirect(post.get_absolute_url())


def create_account(request):
    """Cadastro de novos usuários."""
    if request.user.is_authenticated:
        return redirect("main:home")

    if request.method == "GET":
        return render(request, "base/new_account.html", {"form": UserForm()})

    form = UserForm(request.POST)
    if form.is_valid():
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password"]
        if User.objects.filter(username=username).exists():
            messages.error(request, "Este nome de usuário já está em uso.")
            return render(request, "base/new_account.html", {"form": form})

        user = User.objects.create_user(username=username, password=password)
        login(request, user, backend="django.contrib.auth.backends.ModelBackend")
        messages.success(request, f"Conta criada com sucesso! Bem-vindo(a), {username}!")
        return redirect("main:home")

    return render(request, "base/new_account.html", {"form": form})


class CustomLoginView(LoginView):
    """View customizada de Login com template e mensagens personalizadas."""

    template_name = "base/login.html"

    def get_success_url(self):
        return self.get_redirect_url() or str(reverse_lazy("main:home"))

    def form_invalid(self, form):
        messages.error(self.request, "Nome de usuário ou senha inválidos.")
        return super().form_invalid(form)


def sobre(request):
    """Página institucional Sobre o Blog."""
    return render(request, "base/sobre.html")
