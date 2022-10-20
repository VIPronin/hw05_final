from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .models import Follow, Group, Post, User
from .forms import CommentForm, PostForm
from .utils import get_paginator


@cache_page(20)
def index(request):
    title = 'Главная страница'
    page_obj = get_paginator(request, Post.objects.all())
    context = dict(
        page_obj=page_obj,
        title=title
    )
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    title = 'Посты группы'
    group = get_object_or_404(Group, slug=slug)
    page_obj = get_paginator(request, group.posts.all())
    context = dict(
        group=group,
        page_obj=page_obj,
        title=title
    )
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    title = 'Профиль'
    author = get_object_or_404(User, username=username)
    page_obj = get_paginator(request, author.posts.all())
    following = (Follow.objects.filter(user=request.user,
                                       author=author).exists())
    context = dict(
        author=author,
        following=following,
        page_obj=page_obj,
        title=title
    )
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    title = 'Информация о посте'
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm()
    context = dict(
        post=post,
        title=title,
        comments=post.comments.all(),
        form=form
    )
    return render(request, 'posts/post_detail.html', context)


@login_required()
def post_create(request):
    title = 'Создание нового поста'
    form = PostForm(
        request.POST or None,
        files=request.FILES or None
    )
    context = dict(
        form=form,
        title=title
    )
    if not form.is_valid():
        return render(request, 'posts/create_post.html', context)
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    messages.success(request, 'Пост успешно создан!')
    return redirect('posts:profile', request.user)


@login_required()
def post_edit(request, post_id):
    title = 'Редактирование поста',
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    context = dict(
        form=form,
        post=post,
        title=title,
    )
    messages.success(request,
                     'Что бы сохранить изменение не забудьте '
                     'нажать "СОХРАНИТЬ ЗАПИСЬ!')
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    # Получите пост
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    posts_list = Post.objects.filter(author__following__user=request.user)
    page_obj = get_paginator(request, posts_list)
    context = dict(
        page_obj=page_obj)
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user
    if author != user:
        Follow.objects.get_or_create(user=user, author=author)
    return redirect("posts:profile", username=username)


@login_required
def profile_unfollow(request, username):
    user = request.user
    Follow.objects.filter(user=user, author__username=username).delete()
    return redirect("posts:profile", username=username)
