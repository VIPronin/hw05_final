from django.core.exceptions import ValidationError


def validate_not_follow_twice(value):
# Проверка
    if value == 'author':
        raise ValidationError(
            'Вы уже подписались на этого автора',
            params={'value': value},
        )
