from django.core.exceptions import ValidationError


def validate_not_follow_twice(value):
    if value == 'author':  # Проверка
        raise ValidationError(
            'Вы уже подписались на этого автора',
            params={'value': value},
        )
