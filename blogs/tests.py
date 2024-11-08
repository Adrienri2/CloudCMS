from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Blog, Bookmark, BlogLike, Notification, Category, FavoriteCategory, Report
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from unittest.mock import patch 
from django.template.loader import render_to_string
from django.shortcuts import render
from blogs.views import notifications
from django.test import TransactionTestCase, RequestFactory
from unittest.mock import patch, MagicMock


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


class MarkAsReadViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')
        self.notification = Notification.objects.create(user=self.user, message='Test Notification', is_read=False)

    def test_mark_as_read(self):
        """
        Verifica que la notificación se marque como leída correctamente.
        """
        response = self.client.post(reverse('blogs:mark_as_read', args=[self.notification.id]))
        if response.status_code == 302 and Notification.objects.get(id=self.notification.id).is_read:
            print("La notificación fue marcada como leída con éxito")
        else:
            print("La notificación no pudo ser marcada como leída")
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Notification.objects.get(id=self.notification.id).is_read)

    def test_mark_as_read_requires_login(self):
        """
        Verifica que la vista requiera que el usuario esté autenticado.
        """
        self.client.logout()
        response = self.client.post(reverse('blogs:mark_as_read', args=[self.notification.id]))
        if response.status_code == 302 and response.url.startswith(reverse('accounts:login')):
            print("El usuario no autenticado fue redirigido al inicio de sesión con éxito")
        else:
            print("El usuario no autenticado no fue redirigido correctamente")
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse('accounts:login')))



class ToggleFavoriteCategoryViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.category = Category.objects.create(category='Test Category', category_type='moderada')
        self.client.login(username='testuser', password='12345')

    def test_toggle_favorite_category_add(self):
        """
        Verifica que la categoría se añada a las favoritas del usuario.
        """
        response = self.client.post(reverse('blogs:toggle_favorite_category', args=[self.category.id]))
        if response.status_code == 200 and response.json() == {'status': 'added'} and FavoriteCategory.objects.filter(user=self.user, category=self.category).exists():
            print("El usuario pudo añadir la categoría a favoritos con éxito")
        else:
            print("El usuario no pudo añadir la categoría a favoritos")
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'status': 'added'})
        self.assertTrue(FavoriteCategory.objects.filter(user=self.user, category=self.category).exists())

    def test_toggle_favorite_category_remove(self):
        """
        Verifica que la categoría se elimine de las favoritas del usuario si ya está añadida.
        """
        FavoriteCategory.objects.create(user=self.user, category=self.category)
        response = self.client.post(reverse('blogs:toggle_favorite_category', args=[self.category.id]))
        if response.status_code == 200 and response.json() == {'status': 'removed'} and not FavoriteCategory.objects.filter(user=self.user, category=self.category).exists():
            print("El usuario pudo eliminar la categoría de favoritos con éxito")
        else:
            print("El usuario no pudo eliminar la categoría de favoritos")
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'status': 'removed'})
        self.assertFalse(FavoriteCategory.objects.filter(user=self.user, category=self.category).exists())

    def test_toggle_favorite_category_requires_login(self):
        """
        Verifica que la vista requiera que el usuario esté autenticado.
        """
        self.client.logout()
        response = self.client.post(reverse('blogs:toggle_favorite_category', args=[self.category.id]))
        if response.status_code == 302 and response.url.startswith(reverse('accounts:login')):
            print("El usuario no autenticado fue redirigido al inicio de sesión con éxito")
        else:
            print("El usuario no autenticado no fue redirigido correctamente")
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse('accounts:login')))



class PagoViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.category = Category.objects.create(
            category='Categoría de Prueba',
            slug='categoria-prueba',
            desc='Descripción de prueba',
            is_active=True,
            category_type='moderada',
            subcategory_type='publica',
            costo_membresia=100
        )
        self.client.login(username='testuser', password='12345')

    def test_pago_view_get(self):
        """
        Verifica que la vista PagoView maneje correctamente una solicitud GET.
        """
        url = reverse('blogs:pago', args=[self.category.id])
        response = self.client.get(url)
        templates_used = [template.name for template in response.templates]
        
        if (
            response.status_code == 200 and
            'blogs/pago.html' in templates_used and
            'category' in response.context and
            'datos_tarjeta' in response.context and
            'stripe_publishable_key' in response.context
        ):
            print(f"El usuario '{self.user.username}' pudo acceder a la página de pago correctamente.")
        else:
            print(f"El usuario '{self.user.username}' no pudo acceder a la página de pago como se esperaba.")
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blogs/pago.html')
        self.assertIn('category', response.context)
        self.assertIn('datos_tarjeta', response.context)
        self.assertIn('stripe_publishable_key', response.context)







