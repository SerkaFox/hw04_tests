# posts/tests/test_urls.py
from urllib.parse import urljoin
from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создадим разных пользователей для проверки адресов
        cls.user = User.objects.create_user(username='HasNoName')

        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test_slug',
            description='Описание теста'
        )

        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostURLTests.user)
        self.user = User.objects.create_user(username='Persona')
        self.user_logined = Client()
        self.user_logined.force_login(self.user)
        self.urls_for_guest = {
            reverse(
                'posts:index_p'): HTTPStatus.OK,
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}): HTTPStatus.OK,
            reverse(
                'posts:group_list',
                kwargs={'slug': 'wrong_slug'}): HTTPStatus.NOT_FOUND,
            reverse(
                'posts:profile',
                kwargs={'username': self.user}): HTTPStatus.OK,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}): HTTPStatus.OK,
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}): HTTPStatus.FOUND,
            reverse(
                'posts:post_create'): HTTPStatus.FOUND,
            '/unexisting_page/': HTTPStatus.NOT_FOUND,
        }
        self.urls_for_user = {
            reverse(
                'posts:index_p'): HTTPStatus.OK,
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}): HTTPStatus.OK,
            reverse(
                'posts:group_list',
                kwargs={'slug': 'wrong_slug'}): HTTPStatus.NOT_FOUND,
            reverse(
                'posts:profile',
                kwargs={'username': self.user}): HTTPStatus.OK,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}): HTTPStatus.OK,
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}): HTTPStatus.OK,
            reverse(
                'posts:post_create'): HTTPStatus.OK,
            '/unexisting_page/': HTTPStatus.NOT_FOUND,
        }
        self.urls_templates = {
            reverse(
                'posts:index_p'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': self.user}): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}): 'posts/post_detail.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}): 'posts/create_post.html',
            reverse(
                'posts:post_create'): 'posts/create_post.html',
        }

    def test_unauthorized_user_urls_status_code(self):
        """Проверка status_code для неавторизованного пользователя."""
        for url, response_code in self.urls_for_guest.items():
            with self.subTest(url=url):
                status_code = self.guest_client.get(url).status_code
                self.assertEqual(status_code, response_code)

    def test_authorized_user_urls_status_code(self):
        """Проверка status_code для неавторизованного пользователя."""
        for url, response_code in self.urls_for_user.items():
            with self.subTest(url=url):
                status_code = self.authorized_client.get(url).status_code
                self.assertEqual(status_code, response_code)

    def test_urls_uses_correct_template(self):
        """Проверка status_code для неавторизованного пользователя."""
        for url, template in self.urls_templates.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_redirect_anonymous_on_login(self):
        """Страница /new/ перенаправит анонимного пользователя
        на страницу логина.
        """
        response = self.guest_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}))
        url = urljoin(reverse('login'), f'?next=/posts/{self.post.id}/edit/')
        self.assertRedirects(response, url)

    def test_redirect_client_on_login(self):
        """Страница /new/ перенаправит обычного пользователя
        на страницу логина.
        """
        response = self.user_logined.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}))
        url = reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        self.assertRedirects(response, url)
