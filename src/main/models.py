import uuid
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Post(models.Model):
    """
    Representa uma publicação no Blog.
    """

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="posts",
        verbose_name="Autor",
    )
    title = models.CharField(max_length=200, verbose_name="Título")
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    content = models.TextField(verbose_name="Conteúdo")
    image = models.ImageField(
        upload_to="posts/",
        blank=True,
        null=True,
        verbose_name="Imagem de Capa",
    )
    is_published = models.BooleanField(default=True, verbose_name="Publicado")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Post"
        verbose_name_plural = "Posts"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        if self.slug:
            return reverse("main:post_detail", kwargs={"slug": self.slug})
        return reverse("main:post_detail_pk", kwargs={"pk": self.pk})

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title) or "post"
            unique_slug = base_slug
            counter = 1
            while Post.objects.filter(slug=unique_slug).exclude(pk=self.pk).exists():
                unique_slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = unique_slug
        super().save(*args, **kwargs)

    # Aliases de compatibilidade semântica (PT-BR)
    @property
    def autor(self):
        return self.author

    @property
    def titulo(self):
        return self.title

    @property
    def conteudo(self):
        return self.content

    @property
    def imagem(self):
        return self.image

    @property
    def publicado(self):
        return self.is_published


class Comment(models.Model):
    """
    Representa um comentário em uma publicação do Blog.
    """

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Post",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Autor",
    )
    content = models.TextField(verbose_name="Comentário")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    is_active = models.BooleanField(default=True, verbose_name="Ativo")

    class Meta:
        ordering = ["created_at"]
        verbose_name = "Comentário"
        verbose_name_plural = "Comentários"

    def __str__(self):
        return f"Comentário de {self.author.username} em '{self.post.title}'"

    # Aliases de compatibilidade semântica (PT-BR)
    @property
    def autor(self):
        return self.author

    @property
    def conteudo(self):
        return self.content
