from django import forms

from .constants import NUM_OF_LETTERS
from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {
            'text': ('Текстовочка - помни, пиши красива, '
                     'и да прибудет с тобой сила!!!      *'
                     '** минимальное колличество знаков поста - 10'),
            'group': ('А тут надо выбрать группу - тапни ченить')
        }
        help_texts = {
            'text': ('Какая то полезная инфа для написания поста'),
            'group': ('Если нет подходящей группы - пиши админу'),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        labels = {
            'text': ('Текстовочка      *'
                     '** минимальное колличество знаков коммента - 10'),
        }
        help_texts = {
            'text': ('Какая то полезная инфа для написания коммента'),
        }

    def clean_text(self):
        data = self.cleaned_data['text']
        max_length = len(data)
        if max_length <= NUM_OF_LETTERS:
            raise forms.ValidationError('Кажется ты что забыл сделать! '
                                        'Поле обязательно для заполнения')
        return data
