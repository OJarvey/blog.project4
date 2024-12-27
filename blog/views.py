from django.core.paginator import EmptyPage, Paginator, PageNotAnInteger
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from django.db.models import Count
from django.contrib.postgres.search import (
    SearchVector,
    SearchQuery,
    SearchRank,
)
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.text import slugify
from .models import Post, Comment
from .forms import CommentForm, EmailPostForm, SearchForm, PostForm
from taggit.models import Tag
from django.views.generic import ListView


@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to post a comment.")
        return redirect("account_login")

    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.name = request.user.username
        comment.email = request.user.email
        comment.save()
        return redirect(post.get_absolute_url())

    return render(
        request,
        "blog/post/comment.html",
        {"post": post, "form": form},
    )


def post_list(request, tag_slug=None):
    posts_list = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        posts_list = posts_list.filter(tags__in=[tag])
    paginator = Paginator(posts_list, 3)
    page_number = request.GET.get("page", 1)
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    return render(
        request,
        "blog/post/list.html",
        {"posts": posts, "tag": tag},
    )


def post_detail(request, year, month, day, post):
    post = get_object_or_404(
        Post,
        slug=post,
        status=Post.Status.PUBLISHED,
        publish__year=year,
        publish__month=month,
        publish__day=day,
    )
    comments = post.comments.filter(active=True)
    form = CommentForm()
    post_tags_ids = post.tags.values_list("id", flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(
        id=post.id
    )
    similar_posts = similar_posts.annotate(
        same_tags=Count("tags")
    ).order_by("-same_tags", "-publish")[:4]

    return render(
        request,
        "blog/post/detail.html",
        {
            "post": post,
            "comments": comments,
            "form": form,
            "similar_posts": similar_posts,
        },
    )


def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    sent = False
    if request.method == "POST":
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = (
                f"{cd['name']} ({cd['email']}) recommends you read "
                f"{post.title}"
            )
            message = (
                f"Read {post.title} at {post_url}\n\n"
                f"{cd['name']}'s comments: {cd['comments']}"
            )
            send_mail(
                subject=subject,
                message=message,
                from_email=None,
                recipient_list=[cd["to"]],
            )
            sent = True
    else:
        form = EmailPostForm()

    return render(
        request,
        "blog/post/share.html",
        {"post": post, "form": form, "sent": sent},
    )


def post_search(request):
    form = SearchForm()
    query = None
    results = []
    if "query" in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data["query"]
            search_vector = SearchVector(
                "title", weight="A"
            ) + SearchVector("body", weight="B")
            search_query = SearchQuery(query)

            results = (
                Post.published.annotate(
                    search=search_vector,
                    rank=SearchRank(search_vector, search_query),
                )
                .filter(rank__gte=0.3)
                .order_by("-rank")
            )

    return render(
        request,
        "blog/post/search.html",
        {"form": form, "query": query, "results": results},
    )


@login_required
def post_create(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.slug = slugify(post.title)
            post.save()
            messages.success(request, "Post created successfully!")
            return redirect(post.get_absolute_url())
    else:
        form = PostForm()

    return render(
        request,
        "blog/post/crud/create.html",
        {"form": form},
    )


@login_required
def post_update(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if post.author != request.user:
        raise PermissionDenied("You are not allowed to edit this post.")

    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect(post.get_absolute_url())
    else:
        form = PostForm(instance=post)

    return render(
        request,
        "blog/post/crud/edit.html",
        {"form": form, "post": post},
    )


@login_required
def post_delete(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if post.author != request.user:
        raise PermissionDenied("You are not allowed to delete this post.")

    if request.method == "POST":
        post.delete()
        return redirect("blog:post_list")

    return render(
        request,
        "blog/post/crud/delete.html",
        {"post": post},
    )


class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = "posts"
    paginate_by = 3
    template_name = "blog/post/list.html"
