from django import forms
from django.contrib.auth.models import User
from .models import Post


class AdminPostForm(forms.ModelForm):
    """Formulário administrativo para criação e edição de publicações."""

    class Meta:
        model = Post
        fields = ["title", "author", "content", "image", "is_published"]
        labels = {
            "title": "Título da Publicação",
            "author": "Autor",
            "content": "Conteúdo",
            "image": "Imagem de Capa (opcional)",
            "is_published": "Publicar imediatamente",
        }
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-2.5 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-indigo-500 focus:outline-none",
                    "placeholder": "Título do artigo...",
                }
            ),
            "author": forms.Select(
                attrs={
                    "class": "w-full px-4 py-2.5 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-indigo-500 focus:outline-none",
                }
            ),
            "content": forms.Textarea(
                attrs={
                    "class": "w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-indigo-500 focus:outline-none",
                    "rows": 12,
                    "placeholder": "Conteúdo do artigo...",
                }
            ),
            "image": forms.ClearableFileInput(
                attrs={
                    "class": "w-full px-3 py-2 text-sm text-gray-700 dark:text-gray-300 border border-gray-300 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-700 focus:outline-none",
                }
            ),
            "is_published": forms.CheckboxInput(
                attrs={
                    "class": "w-4 h-4 text-indigo-600 bg-gray-100 border-gray-300 rounded focus:ring-indigo-500 dark:bg-gray-700 dark:border-gray-600",
                }
            ),
        }
