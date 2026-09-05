from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .models import Comment, Post


class BlogModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="author1", password="password123")

    def test_post_creation_and_slug_generation(self):
        post = Post.objects.create(
            author=self.user,
            title="Meu Primeiro Artigo no Blog",
            content="Conteúdo do primeiro post.",
            is_published=True,
        )
        self.assertEqual(post.slug, "meu-primeiro-artigo-no-blog")
        self.assertEqual(str(post), "Meu Primeiro Artigo no Blog")
        self.assertEqual(post.autor, self.user)
        self.assertEqual(post.titulo, "Meu Primeiro Artigo no Blog")
        self.assertEqual(post.conteudo, "Conteúdo do primeiro post.")
        self.assertTrue(post.publicado)

    def test_post_slug_uniqueness(self):
        post1 = Post.objects.create(
            author=self.user,
            title="Post Repetido",
            content="Conteúdo 1",
        )
        post2 = Post.objects.create(
            author=self.user,
            title="Post Repetido",
            content="Conteúdo 2",
        )
        self.assertEqual(post1.slug, "post-repetido")
        self.assertEqual(post2.slug, "post-repetido-1")

    def test_comment_creation_and_properties(self):
        post = Post.objects.create(
            author=self.user,
            title="Post para Comentário",
            content="Conteúdo do post",
        )
        comment = Comment.objects.create(
            post=post,
            author=self.user,
            content="Excelente artigo!",
        )
        self.assertEqual(comment.post, post)
        self.assertEqual(comment.author, self.user)
        self.assertEqual(comment.autor, self.user)
        self.assertEqual(comment.conteudo, "Excelente artigo!")
        self.assertIn("author1", str(comment))


class BlogFeedViewTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username="author", password="password123")
        self.published_post = Post.objects.create(
            author=self.author,
            title="Notícia Pública",
            content="Este post deve aparecer no feed público.",
            is_published=True,
        )
        self.draft_post = Post.objects.create(
            author=self.author,
            title="Rascunho Secreto",
            content="Este post NÃO deve aparecer no feed.",
            is_published=False,
        )

    def test_feed_only_shows_published_posts(self):
        response = self.client.get(reverse("main:home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/home.html")
        posts_in_context = response.context["posts"]
        self.assertIn(self.published_post, posts_in_context)
        self.assertNotIn(self.draft_post, posts_in_context)

    def test_feed_search_filter(self):
        response = self.client.get(reverse("main:home"), {"q": "Notícia"})
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.published_post, response.context["posts"])

        response_empty = self.client.get(reverse("main:home"), {"q": "Inexistente"})
        self.assertEqual(response_empty.status_code, 200)
        self.assertEqual(len(response_empty.context["posts"]), 0)


class PostDetailViewTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username="autor", password="password123")
        self.reader = User.objects.create_user(username="leitor", password="password123")
        self.published_post = Post.objects.create(
            author=self.author,
            title="Post Publicado",
            content="Conteúdo público aberto a todos.",
            is_published=True,
        )
        self.draft_post = Post.objects.create(
            author=self.author,
            title="Post Rascunho",
            content="Conteúdo privado em desenvolvimento.",
            is_published=False,
        )

    def test_public_user_can_view_published_post(self):
        response = self.client.get(self.published_post.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/post_detail.html")
        self.assertContains(response, self.published_post.title)

    def test_anonymous_user_cannot_view_draft(self):
        response = self.client.get(self.draft_post.get_absolute_url())
        self.assertEqual(response.status_code, 404)

    def test_non_author_user_cannot_view_draft(self):
        self.client.force_login(self.reader)
        response = self.client.get(self.draft_post.get_absolute_url())
        self.assertEqual(response.status_code, 404)

    def test_author_can_view_own_draft(self):
        self.client.force_login(self.author)
        response = self.client.get(self.draft_post.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.draft_post.title)
        self.assertContains(response, "Rascunho (Privado)")


class PostCRUDTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username="autor", password="password123")
        self.other_user = User.objects.create_user(username="outro", password="password123")

    def test_create_post_requires_login(self):
        response = self.client.get(reverse("main:post_create"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("main:login"), response.url)

    def test_create_post_authenticated(self):
        self.client.force_login(self.author)
        post_data = {
            "title": "Novo Post Criado",
            "content": "Texto do novo post.",
            "is_published": True,
        }
        response = self.client.post(reverse("main:post_create"), post_data)
        self.assertEqual(response.status_code, 302)
        created_post = Post.objects.get(title="Novo Post Criado")
        self.assertEqual(created_post.author, self.author)
        self.assertEqual(created_post.content, "Texto do novo post.")
        self.assertTrue(created_post.is_published)

    def test_edit_post_by_author(self):
        post = Post.objects.create(
            author=self.author,
            title="Título Original",
            content="Conteúdo Original",
            is_published=True,
        )
        self.client.force_login(self.author)
        edit_data = {
            "title": "Título Modificado",
            "content": "Conteúdo Atualizado",
            "is_published": False,
        }
        response = self.client.post(reverse("main:post_edit", kwargs={"pk": post.pk}), edit_data)
        self.assertEqual(response.status_code, 302)
        post.refresh_from_db()
        self.assertEqual(post.title, "Título Modificado")
        self.assertEqual(post.content, "Conteúdo Atualizado")
        self.assertFalse(post.is_published)

    def test_edit_post_forbidden_for_non_author(self):
        post = Post.objects.create(
            author=self.author,
            title="Título Original",
            content="Conteúdo Original",
        )
        self.client.force_login(self.other_user)
        response = self.client.post(
            reverse("main:post_edit", kwargs={"pk": post.pk}),
            {"title": "Tentativa Invasão", "content": "Novo Conteúdo"},
        )
        self.assertEqual(response.status_code, 403)
        post.refresh_from_db()
        self.assertEqual(post.title, "Título Original")

    def test_delete_post_by_author(self):
        post = Post.objects.create(
            author=self.author,
            title="Post a Deletar",
            content="Conteúdo a Deletar",
        )
        self.client.force_login(self.author)
        response = self.client.post(reverse("main:post_delete", kwargs={"pk": post.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Post.objects.filter(pk=post.pk).exists())

    def test_delete_post_forbidden_for_non_author(self):
        post = Post.objects.create(
            author=self.author,
            title="Post a Deletar",
            content="Conteúdo a Deletar",
        )
        self.client.force_login(self.other_user)
        response = self.client.post(reverse("main:post_delete", kwargs={"pk": post.pk}))
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Post.objects.filter(pk=post.pk).exists())


class CommentTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username="autor", password="password123")
        self.commenter = User.objects.create_user(username="comentarista", password="password123")
        self.intruder = User.objects.create_user(username="intruso", password="password123")
        self.post = Post.objects.create(
            author=self.author,
            title="Post com Comentários",
            content="Conteúdo",
            is_published=True,
        )

    def test_anonymous_cannot_comment(self):
        response = self.client.post(
            reverse("main:comment_create", kwargs={"pk": self.post.pk}),
            {"content": "Comentário anônimo"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Comment.objects.count(), 0)

    def test_authenticated_user_can_comment(self):
        self.client.force_login(self.commenter)
        response = self.client.post(
            reverse("main:comment_create", kwargs={"pk": self.post.pk}),
            {"content": "Muito bom artigo!"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.post.comments.count(), 1)
        comment = self.post.comments.first()
        self.assertEqual(comment.author, self.commenter)
        self.assertEqual(comment.content, "Muito bom artigo!")

    def test_commenter_can_delete_own_comment(self):
        comment = Comment.objects.create(
            post=self.post, author=self.commenter, content="Comentário próprio"
        )
        self.client.force_login(self.commenter)
        response = self.client.post(reverse("main:comment_delete", kwargs={"pk": comment.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Comment.objects.filter(pk=comment.pk).exists())

    def test_post_author_can_delete_any_comment_on_their_post(self):
        comment = Comment.objects.create(
            post=self.post, author=self.commenter, content="Comentário a moderar"
        )
        self.client.force_login(self.author)
        response = self.client.post(reverse("main:comment_delete", kwargs={"pk": comment.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Comment.objects.filter(pk=comment.pk).exists())

    def test_intruder_cannot_delete_other_users_comment(self):
        comment = Comment.objects.create(
            post=self.post, author=self.commenter, content="Comentário legítimo"
        )
        self.client.force_login(self.intruder)
        response = self.client.post(reverse("main:comment_delete", kwargs={"pk": comment.pk}))
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Comment.objects.filter(pk=comment.pk).exists())


class UserPostsDashboardTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="user1", password="password123")
        self.user2 = User.objects.create_user(username="user2", password="password123")
        self.post1 = Post.objects.create(
            author=self.user1, title="Post do User 1", content="Conteúdo 1", is_published=True
        )
        self.draft1 = Post.objects.create(
            author=self.user1, title="Rascunho do User 1", content="Rascunho 1", is_published=False
        )
        self.post2 = Post.objects.create(
            author=self.user2, title="Post do User 2", content="Conteúdo 2", is_published=True
        )

    def test_user_posts_dashboard_shows_own_posts_only(self):
        self.client.force_login(self.user1)
        response = self.client.get(reverse("main:user_posts"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/user_posts.html")
        posts = response.context["posts"]
        self.assertIn(self.post1, posts)
        self.assertIn(self.draft1, posts)
        self.assertNotIn(self.post2, posts)


class AuthAndStaticPagesTests(TestCase):
    def test_create_account(self):
        response = self.client.post(
            reverse("main:create_account"),
            {"username": "novo_autor", "password": "novasenha123"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="novo_autor").exists())

    def test_sobre_page(self):
        response = self.client.get(reverse("main:sobre"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "base/sobre.html")
        self.assertContains(response, "Sobre o Blog")
