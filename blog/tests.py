from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from blog.models import Post, Category, Comment
from django.utils import timezone


class PostViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser', password='password')
        self.category = Category.objects.create(
            name='TestCategory', slug='test-category')
        self.post = Post.objects.create(
            title='Test Post',
            slug='test-post',
            author=self.user,
            category=self.category,
            body='This is a test post body.',
            publish=timezone.now(),
            status=Post.Status.PUBLISHED
        )

    def test_post_list_view(self):
        response = self.client.get(reverse('blog:post_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Post')

    def test_post_detail_view(self):
        url = self.post.get_absolute_url()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Post')


class PostExtraTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser', password='password')
        self.category = Category.objects.create(name='Tech', slug='tech')
        self.post = Post.objects.create(
            title='Extra Test Post',
            slug='extra-test-post',
            author=self.user,
            category=self.category,
            body='This is some extra test content.',
            publish=timezone.now(),
            status=Post.Status.PUBLISHED
        )

    def test_search_view_returns_results(self):
        response = self.client.get(reverse(
            'blog:post_search'), {'query': 'Extra'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Extra Test Post')

    def test_like_post_ajax(self):
        self.client.login(username='testuser', password='password')
        response = self.client.post(
            reverse('blog:post_like', args=[self.post.id]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        self.post.refresh_from_db()
        self.assertIn(self.user, self.post.likes.all())

    def test_comment_submission(self):
        self.client.login(username='testuser', password='password')
        response = self.client.post(
            reverse('blog:post_comment', args=[self.post.id]),
            {'body': 'This is a test comment.'},
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Comment.objects.filter(
            post=self.post, name='testuser').exists())

    def test_create_post_view_authenticated(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('blog:post_create'))
        self.assertEqual(response.status_code, 200)

    def test_post_list_by_category(self):
        response = self.client.get(reverse(
            'blog:post_list_by_category', args=[self.category.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Extra Test Post')
