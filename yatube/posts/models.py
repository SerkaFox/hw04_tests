from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()
COUNT_OF_SORT = 10
COUNT_OF_CUT = 15


class Group(models.Model):
    title = models.CharField(max_length=200,
                             verbose_name='Название группы')
    slug = models.SlugField(unique=True,
                            verbose_name='Условная ссылка на группу')
    description = models.TextField(verbose_name='Описание группы')

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(verbose_name='Текст поста')
    pub_date = models.DateTimeField(auto_now_add=True,
                                    verbose_name='Дата публикации')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор поста'
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        related_name='posts',
        on_delete=models.SET_NULL,
        verbose_name='Группа поста'
    )

    def __str__(self):
        # выводим текст поста
        return self.text[:COUNT_OF_CUT]

    class Meta:
        ordering = ['-pub_date']
