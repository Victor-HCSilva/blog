from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from .models import Comment, Post


class AdminPanelAccessControlTests(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username="admin_user",
            password="admin_password123",
            is_staff=True,
            is_superuser=True,
        )
        self.staff_user = User.objects.create_user(
            username="staff_user",
            password="staff_password123",
            is_staff=True,
            is_superuser=False,
        )
        self.regular_user = User.objects.create_user(
            username="regular_user",
            password="regular_password123",
            is_staff=False,
            is_superuser=False,
        )

    def test_anonymous_user_redirected_to_login(self):
        """Usuário anônimo deve ser redirecionado para a tela de login."""
        response = self.client.get(reverse("admin_panel:dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("main:login"), response.url)
        self.assertIn("next=", response.url)

    def test_regular_user_denied_access(self):
        """Usuário comum autenticado não pode acessar e recebe HTTP 403."""
        self.client.force_login(self.regular_user)

        urls_to_test = [
            reverse("admin_panel:dashboard"),
            reverse("admin_panel:post_list"),
            reverse("admin_panel:comment_list"),
            reverse("admin_panel:user_list"),
        ]
        for url in urls_to_test:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 403)

    def test_staff_user_can_access(self):
        """Usuário com is_staff=True tem acesso concedido."""
        self.client.force_login(self.staff_user)
        response = self.client.get(reverse("admin_panel:dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "admin_panel/dashboard.html")

    def test_superuser_can_access(self):
        """Superusuário tem acesso concedido."""
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse("admin_panel:dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "admin_panel/dashboard.html")


class AdminPanelDashboardTests(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username="admin_user",
            password="admin_password123",
            is_staff=True,
            is_superuser=True,
        )
        self.author = User.objects.create_user(username="author1", password="password123")

        self.p1 = Post.objects.create(author=self.author, title="Post 1", content="C1", is_published=True)
        self.p2 = Post.objects.create(author=self.author, title="Post 2", content="C2", is_published=True)
        self.p3 = Post.objects.create(author=self.author, title="Post 3", content="C3", is_published=False)

        self.c1 = Comment.objects.create(post=self.p1, author=self.author, content="Comentário 1")
        self.c2 = Comment.objects.create(post=self.p1, author=self.admin_user, content="Comentário 2")

    def test_dashboard_stats_and_content(self):
        """Dashboard carrega e exibe contadores corretos."""
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse("admin_panel:dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "admin_panel/dashboard.html")

        self.assertEqual(response.context["total_posts"], 3)
        self.assertEqual(response.context["published_posts"], 2)
        self.assertEqual(response.context["draft_posts"], 1)
        self.assertEqual(response.context["total_comments"], 2)
        self.assertEqual(response.context["total_users"], 2)


class AdminPanelPostManagementTests(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username="admin_user",
            password="admin_password123",
            is_staff=True,
            is_superuser=True,
        )
        self.author1 = User.objects.create_user(username="author1", password="password123")
        self.author2 = User.objects.create_user(username="author2", password="password123")

        self.pub_post = Post.objects.create(
            author=self.author1,
            title="Post Publicado 1",
            content="Conteúdo Publicado",
            is_published=True,
        )
        self.draft_post = Post.objects.create(
            author=self.author2,
            title="Post Rascunho 2",
            content="Conteúdo Rascunho",
            is_published=False,
        )
        self.client.force_login(self.admin_user)

    def test_post_list_and_filters(self):
        """Listagem de posts e aplicação de filtros."""
        # Todos os posts
        response = self.client.get(reverse("admin_panel:post_list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["posts"]), 2)

        # Filtro: apenas publicados
        response_pub = self.client.get(reverse("admin_panel:post_list"), {"status": "published"})
        self.assertIn(self.pub_post, response_pub.context["posts"])
        self.assertNotIn(self.draft_post, response_pub.context["posts"])

        # Filtro: apenas rascunhos
        response_draft = self.client.get(reverse("admin_panel:post_list"), {"status": "draft"})
        self.assertIn(self.draft_post, response_draft.context["posts"])
        self.assertNotIn(self.pub_post, response_draft.context["posts"])

        # Filtro: por autor
        response_auth1 = self.client.get(reverse("admin_panel:post_list"), {"author": self.author1.pk})
        self.assertIn(self.pub_post, response_auth1.context["posts"])
        self.assertNotIn(self.draft_post, response_auth1.context["posts"])

    def test_post_detail_view(self):
        """Visualização de detalhes de um post."""
        response = self.client.get(reverse("admin_panel:post_detail", kwargs={"pk": self.pub_post.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "admin_panel/posts/detail.html")
        self.assertEqual(response.context["post"], self.pub_post)

    def test_post_edit(self):
        """Administrador consegue editar um post."""
        edit_url = reverse("admin_panel:post_edit", kwargs={"pk": self.draft_post.pk})
        response_get = self.client.get(edit_url)
        self.assertEqual(response_get.status_code, 200)

        response_post = self.client.post(
            edit_url,
            {
                "title": "Título Modificado pelo Admin",
                "author": self.author1.pk,
                "content": "Conteúdo Atualizado com Sucesso",
                "is_published": True,
            },
        )
        self.assertEqual(response_post.status_code, 302)
        self.draft_post.refresh_from_db()
        self.assertEqual(self.draft_post.title, "Título Modificado pelo Admin")
        self.assertEqual(self.draft_post.author, self.author1)
        self.assertTrue(self.draft_post.is_published)

    def test_post_publish_and_unpublish(self):
        """Publicar e despublicar via POST."""
        # Publicar rascunho
        pub_url = reverse("admin_panel:post_publish", kwargs={"pk": self.draft_post.pk})
        res = self.client.post(pub_url)
        self.assertEqual(res.status_code, 302)
        self.draft_post.refresh_from_db()
        self.assertTrue(self.draft_post.is_published)

        # Despublicar
        unpub_url = reverse("admin_panel:post_unpublish", kwargs={"pk": self.draft_post.pk})
        res2 = self.client.post(unpub_url)
        self.assertEqual(res2.status_code, 302)
        self.draft_post.refresh_from_db()
        self.assertFalse(self.draft_post.is_published)

        # GET não deve ser permitido
        res_get = self.client.get(pub_url)
        self.assertEqual(res_get.status_code, 405)

    def test_post_delete_requires_confirmation_and_post(self):
        """Exclusão de post exige confirmação (GET) e confirmação via POST."""
        del_url = reverse("admin_panel:post_delete", kwargs={"pk": self.pub_post.pk})

        # GET exibe tela de confirmação sem deletar
        res_get = self.client.get(del_url)
        self.assertEqual(res_get.status_code, 200)
        self.assertTemplateUsed(res_get, "admin_panel/posts/confirm_delete.html")
        self.assertTrue(Post.objects.filter(pk=self.pub_post.pk).exists())

        # POST deleta definitivamente
        res_post = self.client.post(del_url)
        self.assertEqual(res_post.status_code, 302)
        self.assertFalse(Post.objects.filter(pk=self.pub_post.pk).exists())


class AdminPanelCommentManagementTests(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username="admin_user",
            password="admin_password123",
            is_staff=True,
            is_superuser=True,
        )
        self.author = User.objects.create_user(username="author", password="password123")
        self.post = Post.objects.create(author=self.author, title="Post Teste", content="Conteúdo")
        self.c1 = Comment.objects.create(post=self.post, author=self.author, content="Comentário 1", is_active=True)
        self.c2 = Comment.objects.create(post=self.post, author=self.author, content="Comentário 2", is_active=False)
        self.client.force_login(self.admin_user)

    def test_comment_list_and_filter(self):
        """Listagem de comentários e filtro por status ativo/inativo."""
        res = self.client.get(reverse("admin_panel:comment_list"))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.context["comments"]), 2)

        res_active = self.client.get(reverse("admin_panel:comment_list"), {"status": "active"})
        self.assertIn(self.c1, res_active.context["comments"])
        self.assertNotIn(self.c2, res_active.context["comments"])

        res_inactive = self.client.get(reverse("admin_panel:comment_list"), {"status": "inactive"})
        self.assertIn(self.c2, res_inactive.context["comments"])
        self.assertNotIn(self.c1, res_inactive.context["comments"])

    def test_comment_detail(self):
        """Visualização de detalhes de comentário."""
        res = self.client.get(reverse("admin_panel:comment_detail", kwargs={"pk": self.c1.pk}))
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, "admin_panel/comments/detail.html")
        self.assertEqual(res.context["comment"], self.c1)

    def test_comment_delete_requires_confirmation_and_post(self):
        """Exclusão de comentário exige confirmação e método POST."""
        del_url = reverse("admin_panel:comment_delete", kwargs={"pk": self.c1.pk})

        # GET exibe confirmação sem excluir
        res_get = self.client.get(del_url)
        self.assertEqual(res_get.status_code, 200)
        self.assertTemplateUsed(res_get, "admin_panel/comments/confirm_delete.html")
        self.assertTrue(Comment.objects.filter(pk=self.c1.pk).exists())

        # POST exclui o comentário
        res_post = self.client.post(del_url)
        self.assertEqual(res_post.status_code, 302)
        self.assertFalse(Comment.objects.filter(pk=self.c1.pk).exists())


class AdminPanelUserManagementTests(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username="admin_user",
            password="admin_password123",
            is_staff=True,
            is_superuser=True,
        )
        self.target_user = User.objects.create_user(
            username="target_user",
            password="target_password123",
            is_active=True,
        )
        self.client.force_login(self.admin_user)

    def test_user_list(self):
        """Listagem de usuários cadastrados."""
        res = self.client.get(reverse("admin_panel:user_list"))
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, "admin_panel/users/list.html")
        users_list = res.context["users"]
        self.assertIn(self.admin_user, users_list)
        self.assertIn(self.target_user, users_list)

    def test_user_detail(self):
        """Visualização de detalhes de um usuário."""
        res = self.client.get(reverse("admin_panel:user_detail", kwargs={"pk": self.target_user.pk}))
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, "admin_panel/users/detail.html")
        self.assertEqual(res.context["target_user"], self.target_user)

    def test_toggle_user_status(self):
        """Ativar e desativar usuário com segurança."""
        toggle_url = reverse("admin_panel:user_toggle_status", kwargs={"pk": self.target_user.pk})

        # Desativa
        res = self.client.post(toggle_url)
        self.assertEqual(res.status_code, 302)
        self.target_user.refresh_from_db()
        self.assertFalse(self.target_user.is_active)

        # Reativa
        res2 = self.client.post(toggle_url)
        self.assertEqual(res2.status_code, 302)
        self.target_user.refresh_from_db()
        self.assertTrue(self.target_user.is_active)

    def test_admin_cannot_deactivate_self(self):
        """Administrador não pode desativar a própria conta."""
        toggle_self_url = reverse("admin_panel:user_toggle_status", kwargs={"pk": self.admin_user.pk})
        res = self.client.post(toggle_self_url)
        self.assertEqual(res.status_code, 302)
        self.admin_user.refresh_from_db()
        self.assertTrue(self.admin_user.is_active)


class AdminPanelSecurityAndRegressionTests(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username="admin_user",
            password="admin_password123",
            is_staff=True,
            is_superuser=True,
        )
        self.client_with_csrf = Client(enforce_csrf_checks=True)

    def test_csrf_protection_on_admin_actions(self):
        """Ações que alteram estado rejeitam requisições sem CSRF."""
        self.client_with_csrf.force_login(self.admin_user)
        post = Post.objects.create(author=self.admin_user, title="Post CSRF", content="Teste")

        # Tentativa de exclusão sem token CSRF válido deve resultar em 403 Forbidden
        response = self.client_with_csrf.post(
            reverse("admin_panel:post_delete", kwargs={"pk": post.pk}),
        )
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Post.objects.filter(pk=post.pk).exists())

    def test_public_blog_still_functional(self):
        """Garante que a interface pública do blog continua intacta."""
        post = Post.objects.create(
            author=self.admin_user,
            title="Post Público",
            content="Conteúdo público do blog",
            is_published=True,
        )
        res = self.client.get(reverse("main:home"))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Post Público")

        res_detail = self.client.get(post.get_absolute_url())
        self.assertEqual(res_detail.status_code, 200)
        self.assertContains(res_detail, "Post Público")
