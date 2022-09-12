from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from ..models import Group, Post

from ..forms import PostForm

User = get_user_model()


class FormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.form = PostForm
        cls.user = User.objects.create_user(username='Tester')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.group_2 = Group.objects.create(
            title='Тестовая группа_2',
            slug='test_slug_2',
            description='Тестовое описание_2',
        )

        cls.post = Post.objects.create(
            author=cls.user,
            text='Пост первый',
            group=cls.group,
        )
        cls.post_1 = Post.objects.create(
            author=cls.user,
            text='Пост второй',
            group=cls.group,
        )

    def setUp(self):
        self.guest = Client()
        self.user = Client()
        self.user.force_login(FormTests.post.author)

    def test_create_post_save_auth_user(self):
        """Проверяем сохраняется ли в базе пост"""
        post_count = Post.objects.count()
        form_data = {
            'text': 'Текст поста',
            'group': self.group.id,
        }
        response_quest = self.guest.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=False
        )
        self.assertEqual(response_quest.status_code, HTTPStatus.FOUND)
        self.assertEqual(Post.objects.count(), post_count)
        response = self.user.post(reverse(
            'posts:post_create'), data=form_data, follow=True,)
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': self.post.author}, ))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                group=form_data['group']
            ).exists())
        post = Post.objects.all().first()
        self.assertEqual(post.group, self.group)
        self.assertEqual(post.author, self.post.author)

    def test_editor_posts_save(self):
        """Проверяем редактируется и сохраняется ли в базе пост"""
        form_data_edit = {
            'text': 'Другой пост',
            'group': self.group_2.id,
        }
        response_quest = self.guest.post(
            reverse('posts:post_create'),
            data=form_data_edit,
            follow=False
        )
        post_count = Post.objects.count()
        self.assertEqual(response_quest.status_code, HTTPStatus.FOUND)
        response = self.user.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data_edit,
            follow=True

        )
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id},))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(
            Post.objects.filter(
                text=form_data_edit['text'],
                group=form_data_edit['group'],
                pk=self.post.id,
            )
        )
        self.assertEqual(Post.objects.count(), post_count)
        self.assertTrue(Post.objects.filter(
            text='Другой пост', group=self.group_2))
        self.assertFalse(Post.objects.filter(
            text='Другой пост', group=self.group))

    def test_noname_user_create_post(self):
        """ Проверка создания записи не авторизированным пользователем ."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Здесь бы Вася!',
            'group': self.group.id,
        }
        response = self.guest.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Post.objects.count(), posts_count)

    def test_guest_try_post_two(self):
        """Вторая проверка создания записи
        не авторизированным пользователем."""
        form_data = {
            'text': 'Здесь бы Вася и Коля!',
            'group': self.group.id
        }
        self.guest.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertFalse(Post.objects.filter(
            text='Здесь бы Вася и Коля!').exists())
