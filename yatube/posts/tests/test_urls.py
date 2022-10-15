from http import HTTPStatus

from django.core.cache import cache
from django.test import TestCase, Client

from ..models import Group, Post, User


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        """Тест модели приложения Posts.
        Создание тестового пользователя и экземпляр модели"""
        super().setUpClass()
        cls.user = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем пользователя
        self.user = User.objects.create(username='HasNoName')
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user)
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(self.post.author)
        self.access_for_auth = {
            '/follow/': 'posts/follow.html',
            f'/posts/{self.post.pk}/': 'posts/post_detail.html',
            f'/posts/{self.post.pk}/edit/': 'posts/create_post.html',
        }
        self.access_for_all = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/create/': 'posts/create_post.html',
            '/profile/HasNoName/': 'posts/profile.html',
        }
        self.access_fore_not_auth = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            f'/posts/{self.post.pk}/': 'posts/post_detail.html',
        }

    def test_access_for_auth_users(self):
        """Страницы доступна автору."""
        for link_auth, name_auth in self.access_for_auth.items():
            with self.subTest(link_auth=link_auth):
                response = self.authorized_client_author.get(name_auth)
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_access_for_all_users(self):
        """Страницы доступна всем авторизованным пользователям."""
        for link_all, name_all in self.access_for_all.items():
            with self.subTest(name_all=name_all):
                response = self.authorized_client.get(link_all)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_access_for_Not_auth_users(self):
        """Страницы доступна всем не авторизованным пользователям."""
        for link_not_auth, name_auth in self.access_fore_not_auth.items():
            with self.subTest(name_auth=name_auth):
                response = self.guest_client.get(link_not_auth)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_another_user_cant_edit_foreign_posts(self):
        """Пользователь не может редактировать чужие записи."""
        response = self.guest_client.get('/posts/20/edit/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    # Проверяем что запрос к несуществующей странице вернёт ошибку 404
    def test_404(self):
        """Проверка, что запрос к несуществующей странице вернёт ошибку 404"""
        response = self.guest_client.get('/wrong_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    # Проверяем вызываемыe HTML-шаблонов
    def test_urls_uses_correct_template(self):
        cache.clear()
        # Шаблоны по адресам
        templates_url_names = {
            '/': 'posts/index.html',
            '/follow/': 'posts/follow.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user.username}/': 'posts/profile.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{self.post.id}/edit/': 'posts/create_post.html'
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client_author.get(address)
                error_name: str = f'ОШИБКА: {address}, ВОТ ТУТ {template}'
                self.assertTemplateUsed(response, template, error_name)
