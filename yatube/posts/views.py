from django.shortcuts import render, get_object_or_404, redirect
from .models import Group, Post, User, Comment, Follow
from .forms import PostForm, CommentForm
from django.contrib.auth.decorators import login_required
from .utils import get_paginator
from django.views.decorators.cache import cache_page
from django.contrib import messages


@cache_page(20)
def index(request):
    title = 'Главная страница'
    page_obj = get_paginator(request, Post.objects.all())  # набор записей д
    context = dict(
        page_obj=page_obj,
        title=title
    )
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    title = 'Посты группы'
    group = get_object_or_404(Group, slug=slug)
    page_obj = get_paginator(request, group.posts.all())  # набор записей д
    context = dict(
        group=group,
        page_obj=page_obj,
        title=title
    )
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    title = 'Профиль'
    author = get_object_or_404(User, username=username)
    page_obj = get_paginator(request, author.posts.all())  # набор записе
    context = dict(
        author=author,
        page_obj=page_obj,
        title=title
    )
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    title = 'Информация о посте'
    post = get_object_or_404(Post, pk=post_id)
    comments = Comment.objects.filter(post=post.id)
    form = CommentForm()
    context = dict(
        post=post,
        title=title,
        comments=comments,
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
    post = Post.objects.get(pk=post_id)
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
    post = Post.objects.get(pk=post_id)
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
    return render(request, 'posts/follow.html', context) # мож render разобр


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