from django.test import TestCase, Client
from http import HTTPStatus


class StaticURLTests(TestCase):
    def setUp(self):
        # Устанавливаем данные для тестирования
        # Создаём экземпляр клиента. Он неавторизован.
        self.guest_client = Client()

    def test_author_page(self):
        """Страница author/ доступна любому пользователю."""
        # Отправляем запрос через client, созданный в setUp()
        response = self.guest_client.get('/about/author/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_tech_page(self):
        """Страница author/ доступна любому пользователю."""
        # Отправляем запрос через client, созданный в setUp()
        response = self.guest_client.get('/about/tech/')
        self.assertEqual(response.status_code, HTTPStatus.OK)
