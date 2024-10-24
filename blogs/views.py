from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views import View
from django.db.models import F
from django.urls import reverse
from .models import *
from .models import Notification, Category, FavoriteCategory
from django.http import HttpResponseRedirect, JsonResponse

"""
Este módulo define las vistas para la aplicación de blogs, incluyendo la visualización de blogs, creación de comentarios, respuestas, marcadores y likes.

Funciones:
- get_blog_url(slug): Devuelve la URL de un blog basado en su slug.

Clases:
- BlogView: Vista para mostrar una entrada de blog.
- CreateBookmark: Vista para crear o eliminar un marcador en un blog.
- CreateLike: Vista para crear o eliminar un like en un blog.
- CreateComment: Vista para crear un comentario en un blog.
- CreateReply: Vista para crear una respuesta a un comentario.
"""

def get_blog_url(slug):
    """
    Devuelve la URL de un blog basado en su slug.
    """
    return reverse("blogs:blog", args=[slug])

class BlogView(View):
    """
    Vista para mostrar una entrada de blog.
    """
    def get(self, request, slug):
        """
        Maneja las solicitudes GET para mostrar una entrada de blog específica.
        """
        queryset = Blog.objects.filter(is_active=True, slug=slug)
        blog = get_object_or_404(queryset)
        blog.views = F("views") + 1
        blog.save()
        blog.refresh_from_db()

        context = {
            "blog": blog,
            "comments": blog.comments.filter(is_active=True)
        }
        if request.user.is_authenticated:
            context["bookmarked"] = Bookmark.objects.filter(creator=request.user, blog=blog).first()
            context["liked"] = BlogLike.objects.filter(blog=blog, creator=request.user).first()

        return render(request, "blogs/blog.html", context)

class CreateBookmark(View):
    """
    Vista para crear o eliminar un marcador en un blog.
    """
    def post(self, request):
        """
        Maneja las solicitudes POST para crear o eliminar un marcador en un blog.
        """
        blog = get_object_or_404(Blog.objects.filter(is_active=True, id=request.POST.get("id")))
        bookmarked = Bookmark.objects.filter(creator=request.user, blog=blog).first()
        if bookmarked:
            bookmarked.delete()
            messages.info(request, "Marcador eliminado")
        else:
            b = Bookmark(
                blog = blog,
                creator = request.user
            )
            b.save()
            messages.success(request, "Marcador creado")
        return redirect("blogs:blog", slug=blog.slug)

class CreateLike(View):
    """
    Vista para crear o eliminar un like en un blog.
    """
    def post(self, request):
        """
        Maneja las solicitudes POST para crear o eliminar un like en un blog.
        """
        blog = get_object_or_404(Blog.objects.filter(is_active=True, id=request.POST.get("id")))
        liked = BlogLike.objects.filter(blog=blog, creator=request.user).first()
        if liked:
            liked.delete()
            messages.info(request, "Me gusta eliminado")
        else:
            l = BlogLike(creator=request.user, blog=blog)
            l.save()
            messages.success(request, "Me gusta este blog")
        return redirect('blogs:blog', slug=blog.slug)
    
class CreateComment(View):
    """
    Vista para crear un comentario en un blog.
    """
    def post(self, request):
        """
        Maneja las solicitudes POST para crear un comentario en un blog.
        """
        blog = get_object_or_404(Blog.objects.filter(is_active=True, id=request.POST.get("id")))
        comment = request.POST.get("comment")
        if not comment:
            messages.warning(request, "Comentario requerido")
            return redirect("blogs:blog", slug=blog.slug)
        c = Comment(
            comment = comment,
            creator = request.user,
            blog = blog
        )
        c.save()
        messages.success(request, "Comentario creado")
        return redirect(get_blog_url(blog.slug)+"#comments")

class CreateReply(View):
    """
    Vista para crear una respuesta a un comentario.
    """
    def post(self, request):
        """
        Maneja las solicitudes POST para crear una respuesta a un comentario.
        """
        comment = get_object_or_404(Comment.objects.filter(is_active=True, id=request.POST.get("id")))
        reply = request.POST.get("reply")
        if not reply:
            messages.warning(request, "Respuesta requerida")
            return redirect("blogs:blog", slug=comment.blog.slug)

        r = Reply(
            reply = request.POST.get("reply", ""),
            comment = comment,
            creator = request.user
        )
        r.save()

        messages.success(request, "Respuesta creada")
        return redirect(get_blog_url(comment.blog.slug)+"#comments")
    



@login_required
def notifications(request):
    notifications = Notification.objects.filter(user=request.user, is_read=False)
    notifications_count = notifications.count()
    return render(request, 'notifications.html', {'notifications': notifications, 'notifications_count': notifications_count})

@login_required
def mark_as_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return redirect('manage:kanban')


@login_required
def mark_all_as_read(request):
    notifications = Notification.objects.filter(user=request.user, is_read=False)
    notifications.update(is_read=True)
    # Redirigir a la página anterior usando HTTP_REFERER
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))



@login_required
def toggle_favorite_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    favorite, created = FavoriteCategory.objects.get_or_create(user=request.user, category=category)
    if not created:
        favorite.delete()
        return JsonResponse({'status': 'removed'})
    return JsonResponse({'status': 'added'})

@login_required
def favorite_categories(request):
    favorites = FavoriteCategory.objects.filter(user=request.user)
    return render(request, 'blogs/favorite_categories.html', {'favorites': favorites})