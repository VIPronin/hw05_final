import shutil 
import tempfile

from django import forms
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.constants import POSTS_PER_PAGE
from posts.models import Follow, Group, Post, User


# Создаем временную папку для медиа-файлов;
# на момент теста медиа папка будет переопределена
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


# Для сохранения media-файлов в тестах будет использоваться
# временная папка TEMP_MEDIA_ROOT, а потом мы ее удалим
@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        """Тест модели приложения Posts."""
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Тестовый пост',
        )

    def setUp(self):
        cache.clear()
        # Создаём авторизованный клиент
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(self.post.author)
        self.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        self.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=self.small_gif,
            content_type='image/gif'
        )

    @classmethod 
    def tearDownClass(cls): 
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    # Проверяем используемые шаблоны
    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Собираем в словарь пары "имя_html_шаблона: reverse(name)"
        templates_page_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_posts',
                    kwargs={'slug': 'test-slug'}): 'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username':
                            self.user.username}): 'posts/profile.html',
            reverse('posts:post_detail', 
                    kwargs={'post_id': 
                            self.post.id}): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit',
                    kwargs={'post_id':
                            self.post.id}): 'posts/create_post.html',
        }
        # Проверяем, что при обращении к name
        # вызывается соответствующий HTML-шаблон
        for reverse_name, template in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client_author.get(reverse_name)
                self.assertTemplateUsed(response, template)

    # ЭТАП 2 Начинаю проводить второй тест 2 по словарю context
    def test_posts_page_show_correct_context(self):
        """Шаблон posts сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        post = response.context['page_obj'][0]
        self.assertEqual(post.text, self.post.text)

    def test_posts_Group_page_show_correct_context(self):
        """Шаблон Group сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:group_posts', kwargs={'slug': self.group.slug}))
        post = response.context['page_obj'][0]
        self.assertEqual(post.text, self.post.text)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': self.post.author}))
        post = response.context['page_obj'][0]
        self.assertEqual(post.text, self.post.text)

    def test_posts_group_show_new_page_index(self):
        """Шаблон index - дополнительная проверка при создании поста."""
        response = self.authorized_client.get(
            reverse('posts:index')).context['page_obj']
        self.assertIn(self.post, response)

    def test_posts_group_show_new_page_group_posts(self):
        """Шаблон group_posts - дополнительная проверка при создании поста."""
        response = self.authorized_client.get(
            reverse('posts:group_posts', kwargs={
                'slug': self.group.slug})).context['page_obj']
        self.assertIn(self.post, response)

    def test_posts_group_show_new_page_profile(self):
        """Шаблон profile - дополнительная проверка при создании поста."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={
                'username': self.post.author})).context['page_obj']
        self.assertIn(self.post, response)

    def test_posts_not_in_correct_group(self):
        """Шаблон post - дополнительная проверка при создании поста."""
        self.test_group = Group.objects.create(
            title='новая группа',
            slug='new_slug',
            description='новое тестовое описание',
        )
        response = self.authorized_client.get(
            reverse('posts:group_posts', kwargs={
                'slug': self.test_group.slug})).context['page_obj']
        self.assertNotIn(self.post, response)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}))
        post = {response.context['post'].text: self.post.text,
                response.context['post'].group: self.group,
                response.context['post'].author: self.user.username}
        print(response.context)
        for value, expected in post.items():
            self.assertEqual(post[value], expected)
    #    self.assertEqual(response.context.get('self.post'), self.post.text)

    def test_post_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField}
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                error_name: str = f'ОШИБКА: {value}, ВОТ ТУТ {expected}'
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected, error_name)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client_author.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField}
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                error_name: str = f'ОШИБКА: {value}, ВОТ ТУТ {expected}'
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected, error_name)


class PaginatorTests(TestCase):
    @classmethod
    def setUpClass(cls):
        cache.clear()
        """Тест модели приложения Paginator."""
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.authorized_client = Client()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
        )
        cls.post = []
        for i in range(POSTS_PER_PAGE + 1):
            cls.post.append(
                Post.objects.create(
                    author=cls.user,
                    group=cls.group,
                    text=f'Тестовый пост {i}',))
        cls.pages_with_paginator = (
            reverse('posts:index'),
            reverse('posts:group_posts', kwargs={'slug': 'test-slug'}),
            reverse(
                'posts:profile', kwargs={'username': cls.user.username})
        )

    def test_first_page_contains_ten_records(self):
        for test_with_paginator in self.pages_with_paginator:
            with self.subTest(test_with_paginator=test_with_paginator):
                response = self.authorized_client.get(
                    (test_with_paginator))
                # Проверка: количество постов на первой странице равно 10.
                self.assertEqual(len(
                    response.context['page_obj']), POSTS_PER_PAGE)

    def test_second_page_contains_three_records(self):
        for test_with_paginator in self.pages_with_paginator:
            with self.subTest(test_with_paginator=test_with_paginator):
                # Проверка: на второй странице должно быть три поста.
                response = self.authorized_client.get(
                    (test_with_paginator) + '?page=2')
                self.assertEqual(len(response.context['page_obj']), 1)


class FollowTests(TestCase):
    def setUp(self):
        cache.clear()
        self.client_auth_follower = Client()
        self.client_auth_following = Client()
        self.user_follower = User.objects.create_user(username='follower')
        self.user_following = User.objects.create_user(username='following')
        self.post = Post.objects.create(
            author=self.user_following,
            text='Тестовая запись подписчика'
        )
        self.client_auth_follower.force_login(self.user_follower)
        self.client_auth_following.force_login(self.user_following)
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(self.post.author)

    def test_follow(self):
        """Авторизованный пользователь может подписываться на других"""
        self.client_auth_follower.get(
            reverse('posts:profile_follow',
                    kwargs={'username': self.user_following.username}))
        self.assertEqual(Follow.objects.all().count(), 1)

    def test_unfollow(self):
        """Авторизованный пользователь может отписываться"""
        self.client_auth_follower.get(
            reverse('posts:profile_follow',
                    kwargs={'username': self.user_following.username}))
        self.client_auth_follower.get(
            reverse('posts:profile_unfollow',
                    kwargs={'username': self.user_following.username}))
        self.assertEqual(Follow.objects.all().count(), 0)

    def test_follower_see_new_post(self):
        """запись появляется в ленте подписчиков"""
        Follow.objects.create(user=self.user_follower,
                              author=self.user_following)
        response = self.client_auth_follower.get(reverse('posts:follow_index'))
        post_text_0 = response.context["page_obj"][0].text
        self.assertEqual('Тестовая запись подписчика', post_text_0)


class CacheTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post = Post.objects.create(
            author=User.objects.create_user(username='test_name'),
            text='Тестовая запись для создания поста')

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='cherry')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_cache_index(self):
        """Тест кэширования страницы index.html"""
        first_state = self.authorized_client.get(reverse('posts:index'))
        post_1 = Post.objects.get(pk=1)
        post_1.text = 'Измененный текст'
        post_1.save()
        second_state = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(first_state.content, second_state.content)
        cache.clear()
        third_state = self.authorized_client.get(reverse('posts:index'))
        self.assertNotEqual(first_state.content, third_state.content)
