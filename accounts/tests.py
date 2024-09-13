from django.test import TestCase
from django.urls import reverse
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