from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post, COUNT_OF_CUT

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )
        cls.field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор поста'
        }

    def test_models_have_correct_object_names_group(self):
        """Проверяем, что у моделей корректно работает __str__."""
        group = PostModelTest.group
        self.assertEqual(group.title, str(group))

        posts = PostModelTest.post
        self.assertEqual(posts.text[:COUNT_OF_CUT], str(posts))

    def test_verbose_name(self):
        """Проверяем что verbose_name в полях совпадает с ожидаемым."""
        for field, expected_value in self.field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).verbose_name,
                    expected_value)

    def test_post_help_text(self):
        """Проверка help_text у post."""
        feild_help_texts = {
            'text': '',
            'group': '', }
        for value, expected in feild_help_texts.items():
            with self.subTest(value=value):
                help_text = self.post._meta.get_field(value).help_text
                self.assertEqual(help_text, expected)