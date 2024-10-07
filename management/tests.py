from django.test import TestCase
from django.urls import reverse
from blogs.models import Blog, Category
from accounts.models import User
from django.core.files.uploadedfile import SimpleUploadedFile

class KanbanViewTest(TestCase):
    def setUp(self):
        # Crear usuarios con diferentes roles
        self.author_user = User.objects.create_user(username='author', password='password', role='author')
        self.editor_user = User.objects.create_user(username='editor', password='password', role='editor')
        self.publisher_user = User.objects.create_user(username='publisher', password='password', role='publisher')
        self.admin_user = User.objects.create_user(username='admin', password='password', role='admin')

        # Crear categorías con diferentes tipos
        self.moderated_category = Category.objects.create(category='Categoría Moderada', category_type='moderada')
        self.non_moderated_category = Category.objects.create(category='Categoría No Moderada', category_type='no_moderada')

        # Crear una imagen simulada para los thumbnails
        image = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'',  # Puedes proporcionar contenido binario válido si es necesario
            content_type='image/jpeg'
        )

        # Datos comunes para los blogs
        common_blog_data = {
            'desc': 'Descripción de prueba',
            'content': 'Contenido de prueba',
            'thumbnail': image,
        }

        # Función auxiliar para crear blogs
        def create_blog(slug, title, status, creator, is_published=False):
            blog = Blog(
                slug=slug,
                title=title,
                status=status,
                creator=creator,
                is_active=True,
                category=self.moderated_category,
                is_published=is_published,
                **common_blog_data
            )
            blog.save()  # Guarda sin usar force_insert=True
            return blog

        # Blogs para el autor en categoría moderada
        create_blog('borrador-autor', 'Borrador Autor', 0, self.author_user)
        create_blog('en-edicion-autor', 'En Edición Autor', 1, self.author_user)
        create_blog('en-espera-autor', 'En Espera Autor', 2, self.author_user)
        create_blog('publicado-autor', 'Publicado Autor', 3, self.author_user, is_published=True)

        # Blogs para el editor en categoría moderada
        create_blog('en-edicion-editor', 'En Edición Editor', 1, self.editor_user)
        create_blog('en-espera-editor', 'En Espera Editor', 2, self.editor_user)

        # Blogs para el publicador en categoría moderada
        create_blog('en-espera-publisher', 'En Espera Publisher', 2, self.publisher_user)
        create_blog('publicado-publisher', 'Publicado Publisher', 3, self.publisher_user, is_published=True)

        # Blogs para el administrador en categoría moderada
        create_blog('borrador-admin', 'Borrador Admin', 0, self.admin_user)
        create_blog('en-edicion-admin', 'En Edición Admin', 1, self.admin_user)
        create_blog('en-espera-admin', 'En Espera Admin', 2, self.admin_user)
        create_blog('publicado-admin', 'Publicado Admin', 3, self.admin_user, is_published=True)

    def test_author_with_moderated_category(self):
        try:
            self.client.login(username='author', password='password')
            response = self.client.get(reverse('manage:kanban'), {'category_type': 'moderada'})
            self.assertEqual(response.status_code, 200)
            blogs_by_status = response.context['blogs_by_status']
            expected_statuses = ['Borrador', 'En edición', 'En espera', 'Publicado']
            self.assertEqual(sorted(blogs_by_status.keys()), sorted(expected_statuses))
            print("El autor pudo acceder correctamente a la vista Kanban con categoría moderada.")
        except AssertionError:
            print("El autor no pudo acceder correctamente a la vista Kanban con categoría moderada.")
            raise

    def test_editor_with_moderated_category(self):
        try:
            self.client.login(username='editor', password='password')
            response = self.client.get(reverse('manage:kanban'), {'category_type': 'moderada'})
            self.assertEqual(response.status_code, 200)
            blogs_by_status = response.context['blogs_by_status']
            expected_statuses = ['En edición', 'En espera']
            self.assertEqual(sorted(blogs_by_status.keys()), sorted(expected_statuses))
            print("El editor pudo acceder correctamente a la vista Kanban con categoría moderada.")
        except AssertionError:
            print("El editor no pudo acceder correctamente a la vista Kanban con categoría moderada.")
            raise

    def test_publisher_with_moderated_category(self):
        try:
            self.client.login(username='publisher', password='password')
            response = self.client.get(reverse('manage:kanban'), {'category_type': 'moderada'})
            self.assertEqual(response.status_code, 200)
            blogs_by_status = response.context['blogs_by_status']
            expected_statuses = ['En espera', 'Publicado']
            self.assertEqual(sorted(blogs_by_status.keys()), sorted(expected_statuses))
            print("El publicador pudo acceder correctamente a la vista Kanban con categoría moderada.")
        except AssertionError:
            print("El publicador no pudo acceder correctamente a la vista Kanban con categoría moderada.")
            raise

    def test_admin_with_moderated_category(self):
        try:
            self.client.login(username='admin', password='password')
            response = self.client.get(reverse('manage:kanban'), {'category_type': 'moderada'})
            self.assertEqual(response.status_code, 200)
            blogs_by_status = response.context['blogs_by_status']
            expected_statuses = ['Borrador', 'En edición', 'En espera', 'Publicado']
            self.assertEqual(sorted(blogs_by_status.keys()), sorted(expected_statuses))
            print("El administrador pudo acceder correctamente a la vista Kanban con categoría moderada.")
        except AssertionError:
            print("El administrador no pudo acceder correctamente a la vista Kanban con categoría moderada.")
            raise

    def test_author_without_category_type(self):
        try:
            self.client.login(username='author', password='password')
            response = self.client.get(reverse('manage:kanban'))
            self.assertEqual(response.status_code, 200)
            blogs_by_status = response.context['blogs_by_status']
            # La vista agrega 'Borrador' y 'Publicado' con QuerySets vacíos cuando no se proporciona 'category_type'
            expected_statuses = ['Borrador', 'Publicado']
            self.assertEqual(sorted(blogs_by_status.keys()), sorted(expected_statuses))
            for status, queryset in blogs_by_status.items():
                self.assertFalse(queryset.exists(), f"Se esperaba que no hubiera blogs en el estado '{status}'")
            print("El autor pudo acceder correctamente a la vista Kanban sin especificar tipo de categoría.")
        except AssertionError:
            print("El autor no pudo acceder correctamente a la vista Kanban sin especificar tipo de categoría.")
            raise

    def test_admin_without_category_type(self):
        try:
            self.client.login(username='admin', password='password')
            response = self.client.get(reverse('manage:kanban'))
            self.assertEqual(response.status_code, 200)
            blogs_by_status = response.context['blogs_by_status']
            # La vista agrega 'Borrador' y 'Publicado' con QuerySets vacíos cuando no se proporciona 'category_type'
            expected_statuses = ['Borrador', 'Publicado']
            self.assertEqual(sorted(blogs_by_status.keys()), sorted(expected_statuses))
            for status, queryset in blogs_by_status.items():
                self.assertFalse(queryset.exists(), f"Se esperaba que no hubiera blogs en el estado '{status}'")
            print("El administrador pudo acceder correctamente a la vista Kanban sin especificar tipo de categoría.")
        except AssertionError:
            print("El administrador no pudo acceder correctamente a la vista Kanban sin especificar tipo de categoría.")
            raise
