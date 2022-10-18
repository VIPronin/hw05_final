from django.test import Client, TestCase

from posts.models import Group, Post, User

USER_NAME = 'auth'

GROUP_NAME = 'Тестовая группа'
GROUP_DESCRIPTION = 'Тестовое описание'

GROUP_SLUG = 'test-slug'

POST_TEXT = 'Тестовый пост'


class CacheTests(TestCase):
    @classmethod
    def setUpClass(cls):
        """Тест модели приложения Posts."""
        super().setUpClass()
        cls.user = User.objects.create(username=USER_NAME)
        cls.group = Group.objects.create(
            title=GROUP_NAME,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION,
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text=POST_TEXT,
        )

    def setUp(self):
        # Создаём авторизованный клиент
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(self.post.author)

    # Проверяем используемые шаблоны
    def test_cache_index(self):
        """Проверка хранения и authorized_client_author кэша для index."""
