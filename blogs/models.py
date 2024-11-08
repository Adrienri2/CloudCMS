from django.db import models
from accounts.models import User
from django.utils.text import slugify
from ckeditor.fields import RichTextField
from django.conf import settings
from cloudcms.utils import send_notification_email  # Importar la función de envío de correos electrónicos
from cloudinary.models import CloudinaryField  # Importar CloudinaryField


"""
Este módulo define los modelos para la aplicación de blogs, incluyendo categorías, blogs, comentarios, respuestas, marcadores y likes.

Modelos:
- Category: Representa una categoría de blog.
- Blog: Representa una entrada de blog.
- Comment: Representa un comentario en un blog.
- Reply: Representa una respuesta a un comentario.
- Bookmark: Representa un marcador de un blog.
- BlogLike: Representa un like en un blog.
"""

class Category(models.Model):
    """
    Modelo para representar una categoría de blog.
    """

    CATEGORY_TYPE_CHOICES = [
        ('moderada', 'Moderada'),
        ('no_moderada', 'No Moderada'),
    ]

    SUBCATEGORY_TYPE_CHOICES = [
        ('publica', 'Pública'),
        ('suscriptores', 'Para Suscriptores'),
        ('paga', 'De Paga'),
    ]


    category = models.CharField(max_length=30, unique=True)
    slug = models.SlugField(default="", max_length=30)
    desc = models.TextField()
    is_active = models.BooleanField(default=True)
    category_type = models.CharField(max_length=20, choices=CATEGORY_TYPE_CHOICES, default='moderada')
    subcategory_type = models.CharField(max_length=20, choices=SUBCATEGORY_TYPE_CHOICES, default='publica')
    costo_membresia = models.IntegerField(default=0)  # Nuevo campo agregado

    def save(self, *args, **kwargs):
        """
        Sobrescribe el método save para generar automáticamente el slug a partir del nombre de la categoría si no se proporciona.
        """
        if not self.slug:
            self.slug = slugify(self.category)
        super(Category, self).save(*args, **kwargs)

    def __str__(self):
        """
        Devuelve una representación en cadena del objeto Category.
        """
        return self.category


class PaidMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    category_desc = models.TextField()
    category_type = models.CharField(max_length=20)
    subcategory_type = models.CharField(max_length=20)
    membership_cost = models.IntegerField()
    payment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.category.category}"
    


class MembershipPayment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    category_type = models.CharField(max_length=20)
    membership_cost = models.IntegerField()
    payment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.category.category} - {self.payment_date}"
    

class Blog(models.Model):
    """
    Modelo para representar una entrada de blog.
    """
    STATUS_CHOICES = [
        (0, 'Borrador'),
        (1, 'En edición'),
        (2, 'En espera'),
        (3, 'Publicado'),
    ]

    slug = models.SlugField(unique=True, null=False, blank=False, max_length=100)
    title = models.CharField(max_length=100)
    desc = models.TextField()
    content = RichTextField()
    if settings.DEBUG:
        thumbnail = models.ImageField(upload_to='thumbnails/')
    else:
        thumbnail = CloudinaryField('image')
    views = models.IntegerField(default=0)
    category = models.ForeignKey(Category, related_name="blogs", on_delete=models.CASCADE, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_published = models.BooleanField(default=False)
    published_on = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(to=User, on_delete=models.SET_NULL, related_name="blogs", null=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    status_comments = models.TextField(blank=True, null=True)
    previous_status = models.IntegerField(null=True, blank=True)  # Añadido para almacenar el estado previo
    last_modified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='modified_blogs')
    last_modified_by_role = models.CharField(max_length=50, blank=True, null=True)
    scheduled_date = models.DateTimeField(null=True, blank=True)  # Agregar campo para fecha programada
    expiry_date = models.DateTimeField(null=True, blank=True)  # Agregar campo para fecha de caducidad
    is_featured = models.BooleanField(default=False)  # Añadido campo para destacar blogs
    featured_at = models.DateTimeField(null=True, blank=True)  # Añadido campo para fecha de destacado
    one_star_ratings = models.IntegerField(default=0)
    two_star_ratings = models.IntegerField(default=0)
    three_star_ratings = models.IntegerField(default=0)
    
    
    

    

    def __str__(self):
        """
        Devuelve una representación en cadena del objeto Blog.
        """
        return self.title

    def save(self, *args, **kwargs):
        """
         Sobrescribe el método save para asignar el slug como el id del blog después de guardarlo y generar notificaciones.
        """

        is_new = self.pk is None
        old_status = None
        if not is_new:
            old_status = Blog.objects.get(pk=self.pk).status

        super(Blog, self).save(*args, **kwargs)

        if not self.slug:
            self.slug = str(self.id)
        super(Blog, self).save(*args, **kwargs)

        # Generar notificaciones si el estado ha cambiado
        if is_new or old_status != self.status:
            print(f"Estado cambiado de {old_status} a {self.status}")  # Mensaje de depuración
            self.generate_notifications(old_status)


    def generate_notifications(self, old_status):
        """
        Genera notificaciones basadas en el cambio de estado del blog.
        """
        users_to_notify = set()

        if self.status == 0:
            if old_status == 1:
                message = f'Su blog "{self.title}" fue devuelto al estado borrador. Motivo: {self.status_comments}'
                Notification.objects.create(user=self.creator, message=message, blog=self)
                send_notification_email(self.creator, 'Notificación de Blog', message)  # Enviar correo electrónico
            else:
                if self.creator.has_perm('accounts.can_create_blog'):
                    message = f'Su blog "{self.title}" se encuentra en estado "Borrador".'
                    Notification.objects.create(user=self.creator, message=message, blog=self)
                    send_notification_email(self.creator, 'Notificación de Blog', message)  # Enviar correo electrónico   
        elif self.status == 1:
            if old_status == 2:
                message = f'Su blog "{self.title}" no fue aprobado para su publicación, se encuentra en edición nuevamente.'
                Notification.objects.create(user=self.creator, message=message, blog=self)
                send_notification_email(self.creator, 'Notificación de Blog', message)  # Enviar correo electrónico

                if User.objects.filter(user_permissions__codename='can_edit_blog').exists():
                     editors = User.objects.filter(user_permissions__codename='can_edit_blog')
                     for editor in editors:
                        message = f'El blog "{self.title}" no fue aprobado para su publicación, se encuentra en edición nuevamente. Motivo: {self.status_comments}'
                        Notification.objects.create(user=editor, message=message, blog=self)
                        send_notification_email(editor, 'Notificación de Blog', message)  # Enviar correo electrónico
            else:
                if self.creator.has_perm('accounts.can_create_blog'):
                    message = f'Su blog "{self.title}" ha pasado a estado "En edición".'
                    Notification.objects.create(user=self.creator, message=message, blog=self)
                    send_notification_email(self.creator, 'Notificación de Blog', message)  # Enviar correo electrónico
                if User.objects.filter(user_permissions__codename='can_edit_blog').exists():
                    message = f'Tiene un nuevo blog en estado "Para edición", verifíquelo.'
                    users_to_notify.update(User.objects.filter(user_permissions__codename='can_edit_blog'))
        elif self.status == 2:
            if self.creator.has_perm('accounts.can_create_blog'):
                message = f'Su blog "{self.title}" se encuentra en espera para verificación y posterior publicación.'
                Notification.objects.create(user=self.creator, message=message, blog=self)
                send_notification_email(self.creator, 'Notificación de Blog', message)  # Enviar correo electrónico
            if User.objects.filter(user_permissions__codename='can_publish_blog').exists():
                message = f'Tiene un nuevo blog esperando por su publicación, verifíquelo.'
                users_to_notify.update(User.objects.filter(user_permissions__codename='can_publish_blog'))
        elif self.status == 3:
            if self.creator.has_perm('accounts.can_create_blog'):
                message = f'Su blog "{self.title}" se ha publicado correctamente.'
                Notification.objects.create(user=self.creator, message=message, blog=self)
                send_notification_email(self.creator, 'Notificación de Blog', message)  # Enviar correo electrónico


        if users_to_notify:
            for user in users_to_notify:
                Notification.objects.create(user=user, message=message, blog=self)
                send_notification_email(user, 'Notificación de Blog', message)  # Enviar correo electrónico





    def can_edit_or_verify(self, user):
        """
        Determina si el usuario puede editar o verificar el blog.
        """
        return (
            (user.has_perm('accounts.can_edit_blog') and self.status == 1) or
            (user.has_perm('accounts.can_publish_blog') and self.status == 2) or
            (user.has_perm('accounts.can_create_blog') and self.status == 0)
        )

    def get_button_text(self, user):
        """
        Devuelve el texto del botón basado en los permisos del usuario.
        """
        if user.has_perm('accounts.can_publish_blog'):
            return "Verificar"
        return "Editar"


class Report(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='reports')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reporte de {self.user.username} sobre {self.blog.title}"


class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    rating = models.IntegerField()

    class Meta:
        unique_together = ('user', 'blog')
        
 
class BlogVersion(models.Model):
    """
    Modelo para representar una versión de un blog.
    """
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='versions')
    title = models.CharField(max_length=255)
    desc = models.TextField()
    content = models.TextField()
    if settings.DEBUG:
        thumbnail = models.ImageField(upload_to='thumbnails/')
    else:
        thumbnail = CloudinaryField('image')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    modified_by_role = models.CharField(max_length=50)
    return_comment = models.TextField(null=True, blank=True)  # Añadido campo para comentario de devolución
    version_count = models.PositiveIntegerField(default=0)  # Añadir campo para contador de versiones


    def __str__(self):
        return f"Versión de {self.blog.title} creada el {self.created_at}"

    #vamos a probar hacer aqui el contador:
    def save(self, *args, **kwargs):
        if not self.pk:  # Si la instancia es nueva
            last_version = BlogVersion.objects.filter(blog=self.blog).order_by('-version_count').first()
            if last_version:
                self.version_count = last_version.version_count + 1
            else:
                self.version_count = 1
        super(BlogVersion, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Disminuir el contador de versiones de las versiones posteriores
        BlogVersion.objects.filter(blog=self.blog, version_count__gt=self.version_count).update(version_count=models.F('version_count') - 1)
        super(BlogVersion, self).delete(*args, **kwargs)



class Comment(models.Model):
    """
    Modelo para representar un comentario en un blog.
    """
    comment = models.TextField()
    likes = models.IntegerField(default=0)
    blog = models.ForeignKey(to=Blog, on_delete=models.SET_NULL, related_name="comments", null=True)
    creator = models.ForeignKey(to=User, on_delete=models.SET_NULL, related_name="comments", null=True)
    published_on = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        """
        Devuelve una representación en cadena del objeto Comment.
        """
        return self.comment

class Reply(models.Model):
    """
    Modelo para representar una respuesta a un comentario.
    """
    reply = models.TextField()
    likes = models.IntegerField(default=0)
    comment = models.ForeignKey(to=Comment, on_delete=models.SET_NULL, related_name="replies", null=True, blank=True)
    creator = models.ForeignKey(to=User, on_delete=models.SET_NULL, related_name="replies", null=True)
    published_on = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        """
        Devuelve una representación en cadena del objeto Reply.
        """
        return self.reply

class Bookmark(models.Model):
    """
    Modelo para representar un marcador de un blog.
    """
    blog = models.ForeignKey(to=Blog, on_delete=models.SET_NULL, related_name="bookmarks", null=True, blank=True)
    creator = models.ForeignKey(to=User, on_delete=models.SET_NULL, related_name="bookmarks", null=True, blank=True)
    created_on = models.DateField(auto_now_add=True)

    def __str__(self):
        """
        Devuelve una representación en cadena del objeto Bookmark.
        """
        return f"Bookmark({self.id}, {self.creator.username})"

class BlogLike(models.Model):
    """
    Modelo para representar un like en un blog.
    """
    blog = models.ForeignKey(to=Blog, on_delete=models.SET_NULL, related_name="likes", null=True, blank=True)
    creator = models.ForeignKey(to=User, on_delete=models.SET_NULL, related_name="likes", null=True, blank=True)

    def __str__(self):
        """
        Devuelve una representación en cadena del objeto BlogLike.
        """
        return f"BlogLike({self.id}, {self.creator.username})"


class Notification(models.Model):
    """
    Modelo para representar una notificación.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
            return f"Notification for {self.user.username} - {self.message}"



class FavoriteCategory(models.Model):
    """
    Modelo para representar una categoría favorita de un usuario.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_categories')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'category')  # Asegura que un usuario no pueda marcar la misma categoría como favorita más de una vez

    def __str__(self):
        return f"{self.user.username} - {self.category.category}"
