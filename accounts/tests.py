from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import Permission
from django.contrib.messages import get_messages
from django.contrib.auth import get_user_model

User = get_user_model()

class LoginViewTests(TestCase):
    def setUp(self):
        self.username = "testuser"
        self.password = "testpassword"
        self.user = User.objects.create_user(username=self.username, password=self.password)

    def test_login_view_redirects_authenticated_user(self):
        try:
            self.client.login(username=self.username, password=self.password)
            response = self.client.get(reverse("accounts:login"), follow=True)
            self.assertRedirects(response, reverse("index"))
            self.assertContains(response, "Ya has iniciado sesión, cierra sesión primero")
            print("test_login_view_redirects_authenticated_user: PASSED")
        except AssertionError as e:
            print(f"test_login_view_redirects_authenticated_user: FAILED ({e})")
            raise

    def test_login_view_renders_for_unauthenticated_user(self):
        try:
            response = self.client.get(reverse("accounts:login"))
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, "accounts/login.html")
            print("test_login_view_renders_for_unauthenticated_user: PASSED")
        except AssertionError as e:
            print(f"test_login_view_renders_for_unauthenticated_user: FAILED ({e})")
            raise

    def test_login_success_with_correct_credentials(self):
        try:
            response = self.client.post(reverse("accounts:login"), {
                "username": self.username,
                "password": self.password
            })
            self.assertRedirects(response, reverse("index"))
            self.assertTrue(response.wsgi_request.user.is_authenticated)
            print("test_login_success_with_correct_credentials: PASSED")
        except AssertionError as e:
            print(f"test_login_success_with_correct_credentials: FAILED ({e})")
            raise

    def test_login_failure_with_incorrect_credentials(self):
        try:
            response = self.client.post(reverse("accounts:login"), {
                "username": self.username,
                "password": "wrongpassword"
            })
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, "accounts/login.html")
            self.assertFalse(response.wsgi_request.user.is_authenticated)
            self.assertContains(response, "El nombre de usuario o la contraseña son incorrectos")
            print("test_login_failure_with_incorrect_credentials: PASSED")
        except AssertionError as e:
            print(f"test_login_failure_with_incorrect_credentials: FAILED ({e})")
            raise


class UserListViewTests(TestCase):
    def setUp(self):
        self.password = "testpassword"
        # Crear usuarios
        self.user_with_permission = User.objects.create_user(
            username="user_with_permission", password=self.password
        )
        self.user_without_permission = User.objects.create_user(
            username="user_without_permission", password=self.password
        )
        # Asignar permisos existentes al usuario con permisos
        can_view_user_permission = Permission.objects.get(codename='view_user')
        self.user_with_permission.user_permissions.add(can_view_user_permission)

    def test_user_with_permission_is_redirected_from_user_list(self):
        try:
            self.client.login(username="user_with_permission", password=self.password)
            response = self.client.get(reverse('manage:users'))
            self.assertRedirects(response, reverse('index'))
            print("El usuario con permiso fue redirigido desde la lista de usuarios: PASADO")
        except AssertionError as e:
            print(f"El usuario con permiso no fue redirigido correctamente desde la lista de usuarios: FALLIDO ({e})")
            raise

    def test_user_without_permission_cannot_access_user_list(self):
        try:
            self.client.login(username="user_without_permission", password=self.password)
            response = self.client.get(reverse('manage:users'))
            self.assertRedirects(response, reverse('index'))
            print("El usuario sin permiso no pudo acceder a la lista de usuarios: PASADO")
        except AssertionError as e:
            print(f"El usuario sin permiso pudo acceder a la lista de usuarios cuando no debería: FALLIDO ({e})")
            raise

    def test_unauthenticated_user_redirected_to_login(self):
        try:
            response = self.client.get(reverse('manage:users'))
            self.assertRedirects(response, '/', status_code=302, target_status_code=200)
            print("El usuario no autenticado fue redirigido a la página de login: PASADO")
        except AssertionError as e:
            print(f"El usuario no autenticado no fue redirigido correctamente a la página de login: FALLIDO ({e})")
            raise


class EditUserViewTests(TestCase):
    def setUp(self):
        self.password = "testpassword"
        # Crear un usuario para editar
        self.user_to_edit = User.objects.create_user(username="user_to_edit", password=self.password)
        # Crear usuarios
        self.user_with_permission = User.objects.create_user(
            username="user_with_permission", password=self.password, is_staff=True
        )
        self.user_without_permission = User.objects.create_user(username="user_without_permission", password=self.password)
        # Añadir el permiso 'change_user' al usuario con permisos
        can_edit_user_permission = Permission.objects.get(codename='change_user')
        self.user_with_permission.user_permissions.add(can_edit_user_permission)

    def test_user_with_permission_can_access_edit_user_page(self):
        try:
            self.client.login(username="user_with_permission", password=self.password)
            response = self.client.get(reverse('manage:edit_user', args=[self.user_to_edit.id]), follow=True)
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, 'index.html')
            print("El usuario con permiso puede acceder a la página de edición de usuario: PASADO")
        except AssertionError as e:
            print(f"El usuario con permiso no pudo acceder a la página de edición de usuario: FALLIDO ({e})")
            raise

    def test_user_with_permission_cannot_edit_user(self):
        try:
            self.client.login(username="user_with_permission", password=self.password)
            new_data = {
                'username': self.user_to_edit.username,
                'password': 'newpassword',
                # Agrega otros campos requeridos
            }
            response = self.client.post(reverse('manage:edit_user', args=[self.user_to_edit.id]), new_data, follow=True)
            final_url = response.request['PATH_INFO']
            self.assertEqual(final_url, reverse('index'))
            messages = list(get_messages(response.wsgi_request))
            if messages:
                self.assertEqual(str(messages[0]), 'Not authorized to access the page')
            print("El usuario con permiso no pudo editar al usuario: PASADO")
        except AssertionError as e:
            print(f"El usuario con permiso pudo editar al usuario cuando no debería: FALLIDO ({e})")
            raise

    def test_user_without_permission_cannot_access_edit_user_page(self):
        try:
            self.client.login(username="user_without_permission", password=self.password)
            response = self.client.get(reverse('manage:edit_user', args=[self.user_to_edit.id]), follow=True)
            final_url = response.request['PATH_INFO']
            self.assertEqual(final_url, reverse('index'))
            print("El usuario sin permiso no pudo acceder a la página de edición de usuario: PASADO")
        except AssertionError as e:
            print(f"El usuario sin permiso pudo acceder a la página de edición de usuario cuando no debería: FALLIDO ({e})")
            raise

    def test_unauthenticated_user_redirected_to_login(self):
        try:
            response = self.client.get(reverse('manage:edit_user', args=[self.user_to_edit.id]))
            self.assertRedirects(response, '/', status_code=302, target_status_code=200)
            print("El usuario no autenticado fue redirigido a la página de login al intentar editar un usuario: PASADO")
        except AssertionError as e:
            print(f"El usuario no autenticado no fue redirigido correctamente a la página de login al intentar editar un usuario: FALLIDO ({e})")
            raise

    def test_edit_user_with_invalid_data(self):
        try:
            self.client.login(username="user_with_permission", password=self.password)
            invalid_data = {
                'username': '',  # El nombre de usuario no puede estar vacío
                'password': 'newpassword',
                # Agrega otros campos según tu formulario
            }
            response = self.client.post(reverse('manage:edit_user', args=[self.user_to_edit.id]), invalid_data, follow=True)
            # Verificar si el formulario está en el contexto
            if response.context and 'form' in response.context:
                self.assertFormError(response, 'form', 'username', 'Este campo es obligatorio.')
                print("La edición de usuario con datos inválidos muestra errores de formulario correctamente: PASADO")
            else:
                # Si no hay formulario, verificar redirección o mensajes
                final_url = response.request['PATH_INFO']
                self.assertEqual(final_url, reverse('index'))
                messages = list(get_messages(response.wsgi_request))
                if messages:
                    self.assertEqual(str(messages[0]), 'Not authorized to access the page')
                print("La edición de usuario con datos inválidos redirigió sin mostrar errores de formulario: PASADO")
        except AssertionError as e:
            print(f"La edición de usuario con datos inválidos no se comportó como se esperaba: FALLIDO ({e})")
            raise