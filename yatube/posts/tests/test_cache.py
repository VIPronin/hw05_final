from django.test import Client, TestCase
from posts.models import Group, Post, User


class CacheTests(TestCase):
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
        # Создаём авторизованный клиент
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(self.post.author)

    # Проверяем используемые шаблоны
    def test_cache_index(self):
        """Проверка хранения и authorized_client_author кэша для index."""
