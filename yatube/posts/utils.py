from django.core.paginator import Paginator
from .constants import POSTS_PER_PAGE


def get_paginator(request, posts):
    paginator = Paginator(posts, POSTS_PER_PAGE)  # Показывать по 10  .
    page_number = request.GET.get('page')  # Из URL извл. № стр-знач пар-а
    page_obj = paginator.get_page(page_number)  # набор записей
    return page_obj
