from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Blog, Bookmark, BlogLike
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()

class BlogViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.blog = Blog.objects.create(
            title='Test Blog', 
            slug='test-blog', 
            is_active=True,
            thumbnail=SimpleUploadedFile(name='test_image.jpg', content=b'', content_type='image/jpeg')
        )

    def test_blog_view_success(self):
        try:
            response = self.client.get(reverse('blogs:blog', args=[self.blog.slug]))
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, self.blog.title)
            print("test_blog_view_success passed")
        except AssertionError as e:
            print(f"test_blog_view_success failed: {e}")
            raise

        # Caso de prueba que falla
        try:
            response = self.client.get(reverse('blogs:blog', args=[self.blog.slug]))
            self.assertEqual(response.status_code, 404)  # Esto debería fallar
            print("test_blog_view_success_fail_case passed")
        except AssertionError as e:
            print(f"test_blog_view_success_fail_case failed as expected: {e}")
            raise

    def test_blog_view_not_found(self):
        try:
            response = self.client.get(reverse('blogs:blog', args=['non-existent-slug']))
            self.assertEqual(response.status_code, 404)
            print("test_blog_view_not_found passed")
        except AssertionError as e:
            print(f"test_blog_view_not_found failed: {e}")
            raise

        # Caso de prueba que falla
        try:
            response = self.client.get(reverse('blogs:blog', args=['non-existent-slug']))
            self.assertEqual(response.status_code, 200)  # Esto debería fallar
            print("test_blog_view_not_found_fail_case passed")
        except AssertionError as e:
            print(f"test_blog_view_not_found_fail_case failed as expected: {e}")
            raise

class CreateBookmarkTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
        self.blog = Blog.objects.create(
            title='Test Blog', 
            slug='test-blog', 
            is_active=True,
            thumbnail=SimpleUploadedFile(name='test_image.jpg', content=b'', content_type='image/jpeg')
        )

    def test_create_bookmark_success(self):
        try:
            response = self.client.post(reverse('blogs:create_bookmark'), {'id': self.blog.id})
            self.assertRedirects(response, reverse('blogs:blog', args=[self.blog.slug]))
            self.assertTrue(Bookmark.objects.filter(creator=self.user, blog=self.blog).exists())
            print("test_create_bookmark_success passed")
        except AssertionError as e:
            print(f"test_create_bookmark_success failed: {e}")
            raise

        # Caso de prueba que falla
        try:
            response = self.client.post(reverse('blogs:create_bookmark'), {'id': self.blog.id})
            self.assertEqual(response.status_code, 404)  # Esto debería fallar
            print("test_create_bookmark_success_fail_case passed")
        except AssertionError as e:
            print(f"test_create_bookmark_success_fail_case failed: {e}")
            raise

    def test_remove_bookmark_success(self):
        try:
            Bookmark.objects.create(creator=self.user, blog=self.blog)
            response = self.client.post(reverse('blogs:create_bookmark'), {'id': self.blog.id})
            self.assertRedirects(response, reverse('blogs:blog', args=[self.blog.slug]))
            self.assertFalse(Bookmark.objects.filter(creator=self.user, blog=self.blog).exists())
            print("test_remove_bookmark_success passed")
        except AssertionError as e:
            print(f"test_remove_bookmark_success failed: {e}")
            raise

        # Caso de prueba que falla
        try:
            Bookmark.objects.create(creator=self.user, blog=self.blog)
            response = self.client.post(reverse('blogs:create_bookmark'), {'id': self.blog.id})
            self.assertEqual(response.status_code, 404)  # Esto debería fallar
            print("test_remove_bookmark_success_fail_case passed")
        except AssertionError as e:
            print(f"test_remove_bookmark_success_fail_case failed: {e}")
            raise

    def test_create_bookmark_not_found(self):
        try:
            response = self.client.post(reverse('blogs:create_bookmark'), {'id': 999})
            self.assertEqual(response.status_code, 404)
            print("test_create_bookmark_not_found passed")
        except AssertionError as e:
            print(f"test_create_bookmark_not_found failed: {e}")
            raise

        # Caso de prueba que falla
        try:
            response = self.client.post(reverse('blogs:create_bookmark'), {'id': 999})
            self.assertEqual(response.status_code, 200)  # Esto debería fallar
            print("test_create_bookmark_not_found_fail_case passed")
        except AssertionError as e:
            print(f"test_create_bookmark_not_found_fail_case failed: {e}")
            raise

class CreateLikeTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
        self.blog = Blog.objects.create(
            title='Test Blog', 
            slug='test-blog', 
            is_active=True,
            thumbnail=SimpleUploadedFile(name='test_image.jpg', content=b'', content_type='image/jpeg')
        )

    def test_create_like_success(self):
        try:
            response = self.client.post(reverse('blogs:create_like'), {'id': self.blog.id})
            self.assertRedirects(response, reverse('blogs:blog', args=[self.blog.slug]))
            self.assertTrue(BlogLike.objects.filter(creator=self.user, blog=self.blog).exists())
            print("test_create_like_success passed")
        except AssertionError as e:
            print(f"test_create_like_success failed: {e}")
            raise

        # Caso de prueba que falla
        try:
            response = self.client.post(reverse('blogs:create_like'), {'id': self.blog.id})
            self.assertEqual(response.status_code, 404)  # Esto debería fallar
            print("test_create_like_success_fail_case passed")
        except AssertionError as e:
            print(f"test_create_like_success_fail_case failed as expected: {e}")
            raise

    def test_remove_like_success(self):
        try:
            BlogLike.objects.create(creator=self.user, blog=self.blog)
            response = self.client.post(reverse('blogs:create_like'), {'id': self.blog.id})
            self.assertRedirects(response, reverse('blogs:blog', args=[self.blog.slug]))
            self.assertFalse(BlogLike.objects.filter(creator=self.user, blog=self.blog).exists())
            print("test_remove_like_success passed")
        except AssertionError as e:
            print(f"test_remove_like_success failed: {e}")
            raise

        # Caso de prueba que falla
        try:
            BlogLike.objects.create(creator=self.user, blog=self.blog)
            response = self.client.post(reverse('blogs:create_like'), {'id': self.blog.id})
            self.assertEqual(response.status_code, 404)  # Esto debería fallar
            print("test_remove_like_success_fail_case passed")
        except AssertionError as e:
            print(f"test_remove_like_success_fail_case failed as expected: {e}")
            raise

    def test_create_like_not_found(self):
        try:
            response = self.client.post(reverse('blogs:create_like'), {'id': 999})
            self.assertEqual(response.status_code, 404)
            print("test_create_like_not_found passed")
        except AssertionError as e:
            print(f"test_create_like_not_found failed: {e}")
            raise

        # Caso de prueba que falla
        try:
            response = self.client.post(reverse('blogs:create_like'), {'id': 999})
            self.assertEqual(response.status_code, 200)  # Esto debería fallar
            print("test_create_like_not_found_fail_case passed")
        except AssertionError as e:
            print(f"test_create_like_not_found_fail_case failed as expected: {e}")
            raise