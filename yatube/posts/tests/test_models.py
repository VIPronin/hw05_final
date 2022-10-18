from django.test import TestCase

from posts.tests.constants import LEN_SIMBOLS_IN_POST

from ..models import Group, Post, User

USER_NAME = 'auth'

GROUP_NAME = 'Тестовая группа'
GROUP_DESCRIPTION = 'Тестовое описание'

GROUP_SLUG = 'test-slug'

POST_TEXT = 'Тестовый пост'


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        """Тест модели приложения Posts.
        Создание тестового пользователя и экземпляр модели"""
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

    def test_verbose_name_Post(self):
        """verbose_name в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
            'image': 'Картинка',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

    def test_help_text_Post(self):
        """help_text в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_help_texts = {
            'text': 'Введите текст поста',
            'group': 'Группа, к которой будет относиться пост',
            'image': 'Картинка с определенными полями',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                error_name: str = f'ОШИБКА: {value}, ВОТ ТУТ {expected}'
                self.assertEqual(
                    post._meta.get_field(value).help_text,
                    expected, error_name)

    def test_models_forGroup_title_names(self):
        '''Проверка заполнения str group'''
        group = PostModelTest.group
        title = group.__str__()
        self.assertEqual(title, group.title)

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        group = PostModelTest.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post = PostModelTest.post
        expected_object_name = post.text
        self.assertEqual(expected_object_name, str(post))

    def test_str_post_len_15sims(self):
        """__str__ - это 15 символов поста."""
        post = PostModelTest.post  # Обратите внимание на синтаксис
        expected_object_name = post.text[:LEN_SIMBOLS_IN_POST]
        self.assertEqual(expected_object_name, str(post))
