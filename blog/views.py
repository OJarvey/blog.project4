from django.core.paginator import EmptyPage, Paginator, PageNotAnInteger
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from django.db.models import Count
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.text import slugify
from .models import Post, Comment, Category
from .forms import CommentForm, EmailPostForm, SearchForm, PostForm
from taggit.models import Tag
from django.http import JsonResponse
from cloudinary.uploader import destroy
from django.views.decorators.csrf import csrf_exempt


@require_POST
def post_comment(request, post_id):
    """Handle comment submission for a post."""
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
        messages.success(request, "Comment posted successfully!")
        return redirect(post.get_absolute_url())
    else:
        messages.error(request, "Error in comment submission. Please check your input.")
    return render(request, "blog/post/comment.html", {"post": post, "form": form})


@login_required
def toggle_comment_status(request, comment_id):
    """Toggle the active status of a comment (UI-based moderation)."""
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user.is_staff or comment.post.author == request.user:
        comment.active = not comment.active
        comment.save()
        messages.success(
            request,
            f"Comment {'activated' if comment.active else 'deactivated'} successfully!",
        )
    else:
        raise PermissionDenied("You are not allowed to moderate this comment.")
    return redirect(comment.post.get_absolute_url())


def post_list_with_categories(request, tag_slug=None):
    """Display posts with category sidebar and custom filtering."""
    posts_list = (
        Post.published.order_by("-publish")
        .select_related("author", "category")
        .prefetch_related("tags")
    )
    tag = None

    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        posts_list = posts_list.filter(tags__in=[tag])

    filter_option = request.GET.get("filter")
    if filter_option == "name":
        posts_list = posts_list.order_by("title")
    elif filter_option == "date":
        posts_list = posts_list.order_by("publish")
    elif filter_option == "trending":
        posts_list = posts_list.annotate(comment_count=Count("comments")).order_by(
            "-comment_count"
        )
    else:
        posts_list = posts_list.order_by("-publish")

    paginator = Paginator(posts_list, 3)
    page_number = request.GET.get("page", 1)
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    categories = Category.objects.all()
    return render(
        request,
        "blog/post/list.html",
        {"posts": posts, "tag": tag, "categories": categories},
    )


def post_detail(request, year, month, day, post):
    """Display post details with comments and similar posts."""
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
    similar_posts = (
        Post.published.filter(tags__in=post_tags_ids)
        .exclude(id=post.id)
        .annotate(same_tags=Count("tags"))
        .order_by("-same_tags", "-publish")[:4]
    )

    likers = post.likes.all()

    return render(
        request,
        "blog/post/detail.html",
        {
            "post": post,
            "comments": comments,
            "form": form,
            "similar_posts": similar_posts,
            "likers": likers,
        },
    )


def post_share(request, post_id):
    """Share a post via email."""
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    sent = False
    if request.method == "POST":
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} ({cd['email']}) recommends you read {post.title}"
            message = f"Read {post.title} at {post_url}\n\n{cd['name']}'s comments: {cd['comments']}"
            send_mail(subject, message, None, [cd["to"]])
            sent = True
    else:
        form = EmailPostForm()
    return render(
        request, "blog/post/share.html", {"post": post, "form": form, "sent": sent}
    )


def post_search(request):
    """Search posts by title or body."""
    form = SearchForm()
    query = None
    results = []
    if "query" in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data["query"]
            search_vector = SearchVector("title", weight="A") + SearchVector(
                "body", weight="B"
            )
            search_query = SearchQuery(query)
            results = (
                Post.published.annotate(
                    search=search_vector, rank=SearchRank(search_vector, search_query)
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
    """Create a new post."""
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                post = form.save(commit=False)
                post.author = request.user
                post.slug = slugify(post.title)
                # Force image transformation on upload
                if "featured_image" in request.FILES:
                    post.featured_image = form.cleaned_data["featured_image"]
                post.save()
                form.save_m2m()
                messages.success(request, "Post created successfully!")
                return redirect(post.get_absolute_url())
            except Exception as e:
                messages.error(request, f"Error saving post: {str(e)}")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = PostForm()

    return render(
        request,
        "blog/post/crud/create.html",
        {"form": form, "categories": Category.objects.all()},
    )


@login_required
def post_update(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if post.author != request.user:
        raise PermissionDenied("You are not allowed to edit this post.")

    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            updated_post = form.save(commit=False)
            updated_post.slug = slugify(updated_post.title)

            remove_image = request.POST.get("featured_image-clear", False)
            new_image = form.cleaned_data.get("featured_image")

            if remove_image:
                if post.featured_image:
                    try:
                        destroy(post.featured_image.public_id)
                    except Exception as e:
                        print("Failed to delete old image:", e)
                updated_post.featured_image = None

            if new_image:
                updated_post.featured_image = new_image

            updated_post.save()
            form.save_m2m()
            messages.success(request, "Post updated successfully!")
            return redirect(updated_post.get_absolute_url())
        else:
            messages.error(request, "Please correct the form errors.")
    else:
        form = PostForm(instance=post)

    return render(request, "blog/post/crud/edit.html", {"form": form, "post": post})


@login_required
def post_delete(request, post_id):
    """Delete a post."""
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        raise PermissionDenied("You are not allowed to delete this post.")
    if request.method == "POST":
        post.delete()
        messages.success(request, "Post deleted successfully!")
        return redirect("blog:post_list")
    return render(request, "blog/post/crud/delete.html", {"post": post})


@csrf_exempt
@require_POST
def delete_temp_image(request):
    public_id = request.POST.get("public_id")
    if public_id:
        result = destroy(public_id)
        return JsonResponse({"status": "deleted", "result": result})
    return JsonResponse(
        {"status": "error", "message": "No public_id provided"}, status=400
    )


def post_list_by_category(request, category_slug):
    """Display posts filtered by category."""
    category = get_object_or_404(Category, slug=category_slug)
    posts_list = Post.published.filter(category=category)
    paginator = Paginator(posts_list, 3)
    page_number = request.GET.get("page", 1)
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    categories = Category.objects.all()
    return render(
        request,
        "blog/post/list.html",
        {"posts": posts, "category": category, "categories": categories},
    )


@login_required
@require_POST
def post_like(request, post_id):
    """Handle liking/unliking a post via AJAX."""
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    user = request.user

    if user in post.likes.all():
        post.likes.remove(user)
        liked = False
    else:
        post.likes.add(user)
        liked = True

    # Get updated likers list
    likers = [liker.username for liker in post.likes.all()]

    return JsonResponse(
        {
            "status": "success",
            "liked": liked,
            "likes_count": post.total_likes(),
            "likers": likers,
        }
    )
