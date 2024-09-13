from django.db import models
from accounts.models import User
from django.utils.text import slugify
from ckeditor.fields import RichTextField

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
    category = models.CharField(max_length=30, unique=True)
    slug = models.SlugField(default="", max_length=30)
    desc = models.TextField()
    is_active = models.BooleanField(default=True)

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

class Blog(models.Model):
    """
    Modelo para representar una entrada de blog.
    """
    slug = models.SlugField(unique=True, null=False, blank=False, max_length=100)
    title = models.CharField(max_length=100)
    desc = models.TextField()
    content = RichTextField()
    thumbnail = models.ImageField(upload_to="thumbnails/%Y/%m/%d/")
    views = models.IntegerField(default=0)
    categories = models.ManyToManyField(Category, related_name="blogs")
    is_active = models.BooleanField(default=True)
    is_published = models.BooleanField(default=True)
    published_on = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(to=User, on_delete=models.SET_NULL, related_name="blogs", null=True)

    def __str__(self):
        """
        Devuelve una representación en cadena del objeto Blog.
        """
        return self.title

    def save(self, *args, **kwargs):
        """
        Sobrescribe el método save para generar automáticamente el slug a partir del título si no se proporciona.
        """
        if not self.slug:
            self.slug = slugify(self.title)
        super(Blog, self).save(*args, **kwargs)

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