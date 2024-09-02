from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext as _

class UserManager(BaseUserManager):
    """
    Este administrador de usuarios personalizado proporciona métodos para
    crear usuarios y superusuarios con campos adicionales.
    """

    def create_user(self, username, password, **extra_fields):
        """
        Crea y guarda un usuario con el nombre de usuario y la contraseña proporcionados.

        Args:
            username (str): El nombre de usuario del nuevo usuario.
            password (str): La contraseña del nuevo usuario.
            **extra_fields: Campos adicionales para el usuario.

        Raises:
            ValueError: Si el nombre de usuario no es proporcionado.

        Returns:
            user: El usuario creado.
        """
        if not username:
            raise ValueError(_('Users must have an username'))
        if email := extra_fields.get("email", ""):
            extra_fields["email"] = self.normalize_email(email)
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, password, **extra_fields):
        """
        Crea y guarda un superusuario con el nombre de usuario y la contraseña proporcionados.

        Args:
            username (str): El nombre de usuario del nuevo superusuario.
            password (str): La contraseña del nuevo superusuario.
            **extra_fields: Campos adicionales para el superusuario.

        Raises:
            ValueError: Si los campos 'is_staff' o 'is_superuser' no son True.

        Returns:
            user: El superusuario creado.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_author', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(username, password, **extra_fields)