from django import forms
from django.contrib.auth.models import User
from .models import Comment, Post


class PostForm(forms.ModelForm):
    """Formulário para criação e edição de publicações."""

    class Meta:
        model = Post
        fields = ["title", "content", "image", "is_published"]
        labels = {
            "title": "Título da Publicação",
            "content": "Conteúdo",
            "image": "Imagem de Capa (opcional)",
            "is_published": "Publicar imediatamente",
        }
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-2.5 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-indigo-500 focus:outline-none",
                    "placeholder": "Digite o título do post...",
                }
            ),
            "content": forms.Textarea(
                attrs={
                    "class": "w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-indigo-500 focus:outline-none",
                    "rows": 12,
                    "placeholder": "Escreva seu texto aqui...",
                }
            ),
            "image": forms.ClearableFileInput(
                attrs={
                    "class": "w-full px-3 py-2 text-sm text-gray-700 dark:text-gray-300 border border-gray-300 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-700 focus:outline-none file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100",
                }
            ),
            "is_published": forms.CheckboxInput(
                attrs={
                    "class": "w-4 h-4 text-indigo-600 bg-gray-100 border-gray-300 rounded focus:ring-indigo-500 dark:bg-gray-700 dark:border-gray-600",
                }
            ),
        }


class CommentForm(forms.ModelForm):
    """Formulário para adição de comentários."""

    class Meta:
        model = Comment
        fields = ["content"]
        labels = {
            "content": "",
        }
        widgets = {
            "content": forms.Textarea(
                attrs={
                    "class": "w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-indigo-500 focus:outline-none resize-y",
                    "rows": 3,
                    "placeholder": "Deixe um comentário sobre esta publicação...",
                }
            ),
        }


class UserForm(forms.ModelForm):
    """Formulário de cadastro de novo usuário."""

    password = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(
            attrs={
                "class": "w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-indigo-500 focus:outline-none",
                "placeholder": "Digite sua senha secreta",
            }
        ),
    )

    class Meta:
        model = User
        fields = ["username", "password"]
        labels = {
            "username": "Nome de Usuário",
        }
        widgets = {
            "username": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-indigo-500 focus:outline-none",
                    "placeholder": "Escolha seu nome de usuário",
                }
            ),
        }
