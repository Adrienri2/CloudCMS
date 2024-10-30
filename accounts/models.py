from django.contrib.auth.models import AbstractUser, Permission
from django.db import models
from django.utils.translation import gettext as _
from .managers import UserManager
from cloudinary.models import CloudinaryField
from django.conf import settings

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

    """
    Aqui se crean los roles que se asignarán a los usuarios.
    """
    ROLE_CHOICES = [
        ('suscriptor', 'suscriptor'),
        ('admin', 'Administrador'),
        ('author', 'Autor'),
        ('editor', 'Editor'),
        ('publisher', 'Publicador'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='suscriptor')
    
    is_author = models.BooleanField(default=False)

    if settings.DEBUG:
        avatar = models.ImageField(upload_to='avatars/', default="avatars/default.jpeg")
    else:
        avatar = CloudinaryField('image', default="avatars/default.jpeg")

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        """
        Aqui se crean los permisos que se asignarán a los usuarios según su rol.
        Si se desea agregar más permisos, se deben agregar a la lista de permisos.
        """
        permissions = [
            ("can_assign_permissions", "Puede asignar permisos"),
            ("can_create_category", "Puede crear categorías"),
            ("can_edit_category", "Puede editar categorías"),
            ("can_delete_category", "Puede eliminar categorías"),
            ("can_create_blog", "Puede crear artículos"),
            ("can_view_blog", "Puede ver artículos"),
            ("can_publish_blog", "Puede publicar artículos"),
            ("can_edit_blog", "Puede editar artículos"),
            ("can_delete_blog", "Puede eliminar artículos"),
            ("can_create_comment", "Puede crear comentarios"),
            ("can_edit_comment", "Puede editar comentarios"),
            ("can_delete_comment", "Puede eliminar comentarios"),
            ("can_view_user", "Puede ver usuarios"),
            ("can_edit_user", "Puede editar usuarios"),
            ("can_delete_user", "Puede eliminar usuarios"),
        ]

    def __str__(self):
        """
        Devuelve una representación en cadena del usuario.

        Returns:
            str: El nombre de usuario del usuario.
        """
        return self.username
    
    def save(self, *args, **kwargs):
        """
        Sobrescribe el método save para asignar permisos basados en el rol del usuario.

        Args:
            *args: Argumentos posicionales.
            **kwargs: Argumentos de palabras clave.
        """
        
        # Verificar si se está guardando desde el formulario de edición
        if kwargs.pop('update_permissions', True):
            super().save(*args, **kwargs)

            """
            Aqui se le asignan los permisos a los usuarios según su rol.
            """

            if self.role == 'author':
                self.user_permissions.add(Permission.objects.get(codename='can_create_blog'))
                self.user_permissions.add(Permission.objects.get(codename='can_delete_blog'))
            elif self.role == 'editor':
                self.user_permissions.add(Permission.objects.get(codename='can_edit_blog'))
            elif self.role == 'publisher':
                self.user_permissions.add(Permission.objects.get(codename='can_publish_blog'))
            elif self.role == 'admin':
                excluded_permissions = ['can_create_blog', 'can_edit_blog', 'can_publish_blog']
                all_permissions = Permission.objects.exclude(codename__in=excluded_permissions)
                self.user_permissions.set(all_permissions)
            elif self.role == 'suscriptor':
                self.user_permissions.clear()
                self.user_permissions.add(Permission.objects.get(codename='can_view_blog'))
        else:
            super().save(*args, **kwargs)
