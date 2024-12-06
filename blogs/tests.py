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
from .views import BlogStatisticsView

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



class BlogStatisticsViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Configurar datos iniciales una vez para todas las pruebas
        cls.factory = RequestFactory()
        cls.user = User.objects.create_user(username='testuser', password='12345')
        cls.category = Category.objects.create(
            category='Test Category',
            category_type='publica'
        )
        # Crear Blogs con slugs ya asignados y asignar un creador
        cls.blogs = []
        with patch('blogs.models.print'):  # Mockea solo los prints en blogs.models
            for i in range(1, 7):
                blog = Blog(
                    title=f'Blog {i}',
                    slug=f'slug-{i}',  # Asigna un slug temporal
                    is_active=True,
                    is_published=True,
                    creator=cls.user  # Asigna el usuario como creador
                )
                blog.save()
                cls.blogs.append(blog)

    @patch('blogs.views.requests.get')
    def test_get_context_data_disqus_success(self, mock_get):
        # Configurar la respuesta mock de Disqus
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'response': [
                {
                    'title': 'Blog 1',
                    'posts': 10,
                    'link': 'http://example.com/blog-1',
                    'isDeleted': False
                },
                {
                    'title': 'Blog 2',
                    'posts': 5,
                    'link': 'http://example.com/blog-2',
                    'isDeleted': False
                },
                {
                    'title': 'Blog 3',
                    'posts': 20,
                    'link': 'http://example.com/blog-3',
                    'isDeleted': False
                },
                {
                    'title': 'Blog 4',
                    'posts': 15,
                    'link': 'http://example.com/blog-4',
                    'isDeleted': False
                },
                {
                    'title': 'Blog 5',
                    'posts': 8,
                    'link': 'http://example.com/blog-5',
                    'isDeleted': False
                },
                {
                    'title': 'Blog 6',
                    'posts': 12,
                    'link': 'http://example.com/blog-6',
                    'isDeleted': True  # Este debe ser excluido
                },
            ]
        }
        mock_get.return_value = mock_response

        # Crear una solicitud GET
        request = self.factory.get(reverse('blogs:blog_statistics'))
        request.user = self.user

        # Instanciar la vista y obtener el contexto
        response = BlogStatisticsView.as_view()(request)
        context = response.context_data

        # Verificar el total de comentarios
        expected_total_comments = 10 + 5 + 20 + 15 + 8  # 58
        self.assertEqual(context['total_comments'], expected_total_comments)
        print("El total de comentarios fue verificado con éxito")

        # Verificar los top 5 blogs
        expected_top_5_filtered = [
            {'title': 'Blog 3', 'posts': 20, 'link': 'http://example.com/blog-3'},
            {'title': 'Blog 4', 'posts': 15, 'link': 'http://example.com/blog-4'},
            {'title': 'Blog 1', 'posts': 10, 'link': 'http://example.com/blog-1'},
            {'title': 'Blog 5', 'posts': 8, 'link': 'http://example.com/blog-5'},
            {'title': 'Blog 2', 'posts': 5, 'link': 'http://example.com/blog-2'},
        ]
        self.assertEqual(context['top_5_blogs'], expected_top_5_filtered)
        print("Los top 5 blogs fueron verificados con éxito")

    @patch('blogs.views.requests.get')
    def test_get_context_data_disqus_failure(self, mock_get):
        # Configurar la respuesta mock para que falle
        mock_get.side_effect = Exception("API Error")

        # Crear una solicitud GET
        request = self.factory.get(reverse('blogs:blog_statistics'))
        request.user = self.user

        # Instanciar la vista y obtener el contexto
        response = BlogStatisticsView.as_view()(request)
        context = response.context_data

        # Verificar que total_comments indique un error y top_5_blogs esté vacío
        expected_error_message = 'Error al obtener los comentarios'
        self.assertEqual(context['total_comments'], expected_error_message)
        print("El manejo de error para total_comments fue verificado con éxito")

        expected_top_blogs = []
        self.assertEqual(context['top_5_blogs'], expected_top_blogs)
        print("El manejo de error para top_5_blogs fue verificado con éxito")

    @patch('blogs.views.requests.get')
    def test_get_context_data_disqus_empty_response(self, mock_get):
        # Configurar una respuesta vacía de Disqus
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'response': []}
        mock_get.return_value = mock_response

        # Crear una solicitud GET
        request = self.factory.get(reverse('blogs:blog_statistics'))
        request.user = self.user

        # Instanciar la vista y obtener el contexto
        response = BlogStatisticsView.as_view()(request)
        context = response.context_data

        # Verificar que total_comments sea 0 y top_5_blogs esté vacío
        self.assertEqual(context['total_comments'], 0)
        print("El total de comentarios vacío fue verificado con éxito")

        expected_top_blogs = []
        self.assertEqual(context['top_5_blogs'], expected_top_blogs)
        print("El top 5 blogs vacío fue verificado con éxito")

        