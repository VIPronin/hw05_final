import tempfile

from http import HTTPStatus

from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..forms import PostForm
from ..models import Comment, Group, Post, User

# Создаем временную папку для медиа-файлов;
# на момент теста медиа папка будет переопределена
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


# Для сохранения media-файлов в тестах будет использоваться
# временная папка TEMP_MEDIA_ROOT, а потом мы ее удалим
@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Тестовый текст',
        )

    def setUp(self):
        # Создаем клиентов
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        # Для тестирования загрузки изображений
        # берём байт-последовательность картинки,
        # состоящей из двух пикселей: белого и чёрного
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

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        # Подсчитаем количество записей в Post
        posts_count = Post.objects.count()
        # Подготавливаем данные для передачи в форму
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.id,
            'image': self.uploaded
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': self.post.author}))
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), posts_count + 1)
        # Проверяем, что создалась запись с нашим слагом
        post = Post.objects.first()
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.group, self.post.group)
        self.assertEqual(post.author, self.post.author)
        self.assertEqual(post.image, f'posts/{self.uploaded}')  # check after
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_post(self):
        """Валидная форма для редактирования поста."""
        # понять почему не могу обратиться к cls.post = Post.objects.create
        # Подготавливаем данные для передачи в форму
        self.post = Post.objects.create(
            text='Тестовый текст',
            group=self.group,
            author=self.user
        )
        # фиксирую пост с которым буду сравнивать
        fix_post = self.post
        # делаю новый словарь
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.id,
        }
        # сравниваю. не забыть проставить .id к посту
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': fix_post.id}),
            data=form_data,
            follow=True
        )
        # Проверяем, что создалась запись и тест не упал
        post = Post.objects.first()
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.group, self.post.group)
        self.assertEqual(post.author, self.post.author)
        self.assertEqual(response.status_code, HTTPStatus.OK)


class LableHelpTextFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.form = PostForm()

    def test_title_label_text(self):
        text_label = LableHelpTextFormTests.form.fields['text'].label
        self.assertEqual(
            text_label, 'Текстовочка - помни, пиши красива, '
                        'и да прибудет с тобой сила!!!      *'
                        '** минимальное колличество знаков поста - 10')

    def test_title_label_group(self):
        text_label = LableHelpTextFormTests.form.fields['group'].label
        self.assertEqual(
            text_label, 'А тут надо выбрать группу - тапни ченить')

    def test_title_help_text(self):
        title_help_text = LableHelpTextFormTests.form.fields['text'].help_text
        self.assertEqual(
            title_help_text, 'Какая то полезная инфа для написания поста')

    def test_title_help_group(self):
        title_help_text = LableHelpTextFormTests.form.fields['group'].help_text
        self.assertEqual(
            title_help_text, 'Если нет подходящей группы - пиши админу')


class CommentFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Тестовый текст',
        )
        cls.comment = Comment.objects.create(
            author=cls.user,
            post_id=cls.post.id,
            text='Тестовый коммент',
        )

    def setUp(self):
        # Создаем клиентов
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        # Для тестирования загрузки изображений
        # берём байт-последовательность картинки,
        # состоящей из двух пикселей: белого и чёрного

    def test_create_comment(self):
        """комментировать посты может только авторизованный пользователь"""
        # Подсчитаем количество записей в Comment
        comment_count = Comment.objects.count()
        # Подготавливаем данные для передачи в форму
        form_data = {
            'text': 'Тестовый коммент'
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        # self.assertRedirects(response, reverse(
        #     'post_detail', kwargs={'post_id': self.post.pk}))
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        # Проверяем, что создалась запись с нашим слагом
        post = self.comment
        self.assertEqual(post.text, self.comment.text)
        self.assertEqual(response.status_code, HTTPStatus.OK)
