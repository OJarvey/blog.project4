from django.test import TestCase
from blog.forms import PostForm, CommentForm
from django.urls import reverse
from blog.models import Post
from django.contrib.auth.models import User
from django.test import SimpleTestCase
from django.urls import reverse, resolve
from blog.views import post_list, post_detail


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
            password="12345")
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
