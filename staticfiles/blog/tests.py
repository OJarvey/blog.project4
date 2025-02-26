from django.test import TestCase, Client, SimpleTestCase
from blog.forms import PostForm, CommentForm
from django.urls import reverse, resolve
from blog.models import Post
from blog.views import post_list, post_detail
from django.contrib.auth.models import User
from django.core.paginator import Paginator


class TestUrls(SimpleTestCase):
    def test_post_list_url(self):
        url = reverse("blog:post_list")
        self.assertEqual(resolve(url).func, post_list)

    def test_post_detail_url(self):
        url = reverse(
            "blog:post_detail",
            args=["2024", "12", "26", "test-post"],
        )
        self.assertEqual(resolve(url).func, post_detail)


class PostFormTest(TestCase):
    def test_valid_post_form(self):
        form = PostForm(
            data={
                "title": "Test Post",
                "tags": "tag1, tag2",
                "body": "This is a test post body.",
            }
        )
        self.assertTrue(form.is_valid())

    def test_invalid_post_form(self):
        form = PostForm(data={"title": ""})  # Missing required fields
        self.assertFalse(form.is_valid())


class CommentFormTest(TestCase):
    def test_valid_comment_form(self):
        form = CommentForm(data={"body": "This is a test comment."})
        self.assertTrue(form.is_valid())


class PostViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="12345",
        )
        self.post = Post.objects.create(
            title="Test Post",
            slug="test-post",
            author=self.user,
            body="This is a test post body.",
            status=Post.Status.PUBLISHED,
        )

    def test_post_list_view(self):
        response = self.client.get(reverse("blog:post_list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/post/list.html")
        self.assertContains(response, self.post.title)

    def test_post_detail_view(self):
        response = self.client.get(
            reverse(
                "blog:post_detail",
                args=[
                    self.post.publish.year,
                    self.post.publish.month,
                    self.post.publish.day,
                    self.post.slug,
                ],
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/post/detail.html")
        self.assertContains(response, self.post.body)


class PostCreateTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="12345",
        )
        self.client = Client()

    def test_create_post_authenticated(self):
        self.client.login(username="testuser", password="12345")
        response = self.client.post(
            reverse("blog:post_create"),
            {
                "title": "New Post",
                "tags": "tag1, tag2",
                "body": "This is a new post body.",
            },
        )
        self.assertEqual(response.status_code, 302)

    def test_create_post_unauthenticated(self):
        response = self.client.post(
            reverse("blog:post_create"),
            {
                "title": "New Post",
                "tags": "tag1, tag2",
                "body": "This is a new post body.",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)


class PostAuthTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="12345",
        )
        self.other_user = User.objects.create_user(
            username="otheruser",
            password="12345",
        )
        self.post = Post.objects.create(
            title="Test Post",
            slug="test-post",
            author=self.user,
            body="This is a test post body.",
            status=Post.Status.PUBLISHED,
        )
        self.client = Client()

    def test_post_create_authenticated(self):
        self.client.login(username="testuser", password="12345")
        response = self.client.get(reverse("blog:post_create"))
        self.assertEqual(response.status_code, 200)

    def test_post_update_authenticated(self):
        self.client.login(username="testuser", password="12345")
        response = self.client.post(
            reverse("blog:post_update", args=[self.post.id]),
            {
                "title": "Updated Title",
                "body": "Updated body",
                "tags": "tag1, tag2",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, "Updated Title")

    def test_post_delete_authenticated(self):
        self.client.login(username="testuser", password="12345")
        response = self.client.post(
            reverse("blog:post_delete", args=[self.post.id])
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Post.objects.filter(id=self.post.id).exists())


class PaginationTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="12345"
        )

        for i in range(15):
            Post.objects.create(
                title=f"Post {i}",
                slug=f"post-{i}",
                author=self.user,
                body=f"This is post {i} body.",
                status=Post.Status.PUBLISHED,
            )

    def test_pagination_first_page(self):
        response = self.client.get(reverse("blog:post_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Post 0")
        self.assertNotContains(response, "Post 10")

    def test_pagination_second_page(self):
        response = self.client.get(reverse("blog:post_list") + "?page=2")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Post 10")


class SearchTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="12345"
        )

        Post.objects.create(
            title="First Test Post",
            slug="first-test-post",
            author=self.user,
            body="Content about Django testing.",
            status=Post.Status.PUBLISHED,
        )

    def test_search_valid_query(self):
        response = self.client.get(
            reverse("blog:post_search"),
            {"query": "Django"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "First Test Post")
