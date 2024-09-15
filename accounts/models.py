from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext as _
from .managers import UserManager

class User(AbstractUser):
    """
    Modelo de usuario personalizado que extiende el modelo de usuario abstracto de Django.

    Atributos:
        is_author (bool): Indica si el usuario es un autor.
        avatar (ImageField): Imagen de avatar del usuario.
        gender (str): Género del usuario.
    """

    GENDER_CHOICES = [
        ('M', 'Varón'),
        ('F', 'Mujer'),
        ('O', 'Otro'),
    ]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True)
    is_author = models.BooleanField(default=False)
    avatar = models.ImageField(upload_to="avatars/", default="avatars/default.jpeg")

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        """
        Devuelve una representación en cadena del usuario.

        Returns:
            str: El nombre de usuario del usuario.
        """
        return self.username