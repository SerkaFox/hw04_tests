# deals/tests/test_views.py
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from ..models import Post, Group

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создадим запись в БД
        # Обычный пользователь
        cls.author = User.objects.create_user(username='Виртуальный Автор')
        # Виртуальная группа
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test_slug',
            description='Описание теста'
        )
        # Виртуальный пост
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.author,
            pub_date=('Дата публикации'),
            group=cls.group
        )

    def setUp(self) -> None:
        self.guest = Client()
        self.user = User.objects.create_user(username='Persona')
        self.user_logined = Client()
        self.user_logined.force_login(self.user)
        self.author_post = Client()
        self.author_post.force_login(self.author)

    def test_templates(self):
        templates_pages_names = {
            reverse('posts:index_p'): 'posts/index.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}
                    ): 'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': self.author}
                    ): 'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post.id}
                    ): 'posts/post_detail.html',
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.id}
                    ): 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(template=template):
                response = self.author_post.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_pages_uses_correct_template_for_guest(self):
        """URL-адрес не использует шаблон для
         не авторизованного пользователя"""
        response = self.guest.get(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}
            )
        )
        self.assertTemplateNotUsed(response, 'posts/create_post.html')

    def test_group_list(self):
        """На страницу group_list передаётся ожидаемое количество объектов."""
        response = self.guest.get(reverse(
            'posts:group_list',
            kwargs={'slug': self.group.slug}))
        context = response.context
        group_list = context['group']
        self.assertEqual(group_list, self.group)

    def test_profile(self):
        """На страницу profile передаётся ожидаемое количество объектов."""
        response = self.author_post.get(reverse(
            'posts:profile',
            kwargs={'username': self.author}))
        context = response.context
        group_list = context['author']
        self.assertEqual(group_list, self.author)

    def test_post_detail(self):
        """На страницу post_detail передаётся ожидаемое количество объектов."""
        response = self.user_logined.get(reverse(
            'posts:post_detail',
            kwargs={'post_id': self.post.id}))
        context = response.context
        group_list = context['post']
        self.assertEqual(group_list, self.post)

    def test_post_edit(self):
        """На страницу group_list передаётся ожидаемое количество объектов."""
        response = self.author_post.get(reverse(
            'posts:post_edit', kwargs={'post_id': self.post.id}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                # Проверяет, что поле формы является экземпляром
                # указанного класса
                self.assertIsInstance(form_field, expected)

    def test_index_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.author_post.get(reverse('posts:index_p'))
        post_context = response.context['page_obj'][0]
        self.assertEqual(self.post.id, post_context.id)
        self.assertEqual(self.post.text, post_context.text)
        self.assertEqual(self.group.id, post_context.group.id)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user2 = User.objects.create_user(username='PagiMan')
        cls.author2 = Client()
        cls.author2.force_login(cls.user2)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user2,
            text='Текст',
            group=cls.group
        )

        cls.posts = []
        for i in range(15):
            cls.posts.append(
                Post(
                    author=cls.user2,
                    text=f'tests{i}',
                    group=cls.group

                )
            )
        Post.objects.bulk_create(cls.posts)
        cls.test_paginator = {
            reverse('posts:index_p'): 'Главная страница',
            reverse('posts:group_list',
                    kwargs={'slug': cls.group.slug}): 'Страница с группами',
            reverse('posts:profile',
                    kwargs={'username': cls.user2}): 'Личная страница'

        }

    def test_first_page_contains_ten_records(self):
        for address, counter in self.test_paginator.items():
            with self.subTest(counter=counter):
                self.assertEqual(len((self.author2.get(
                    address)).context['page_obj']), 10,
                    f'Количество постов на странице {counter} не равно 10')

    def test_second_page_contains(self):
        for address, counter in self.test_paginator.items():
            with self.subTest(counter=counter):
                self.assertEqual(len((self.author2.get(
                    address + '?page=2')).context['page_obj']),
                    Post.objects.count() - 10, f'{counter} пуста')
