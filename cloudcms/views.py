from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.db.models import Q
from django.views.generic import ListView
from blogs.models import Blog, Bookmark, Category
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages

class Index(View):
    """
    Vista para la página de inicio.

    Muestra una lista paginada de blogs activos y publicados, ordenados por número de vistas.

    Métodos:
        get: Renderiza la página de inicio con la lista de blogs paginada.
    """

    def get(self, request):
        """
        Maneja las solicitudes GET para la página de inicio.

        Args:
            request: El objeto de solicitud HTTP.

        Returns:
            HttpResponse: La respuesta HTTP con la página de inicio renderizada.
        """
        blog_list = Blog.objects.filter(is_active=True, is_published=True).order_by("-views")
        page = request.GET.get('page', 1)

        paginator = Paginator(blog_list, 9)
        try:
            blogs = paginator.page(page)
        except PageNotAnInteger:
            blogs = paginator.page(1)
        except EmptyPage:
            blogs = paginator.page(paginator.num_pages)

        context = {
            'blogs': blogs
        }
        return render(request, 'index.html', context)

class Search(ListView):
    """
    Vista para la búsqueda de blogs.

    Muestra una lista paginada de blogs que coinciden con la consulta de búsqueda.

    Atributos:
        model: El modelo de datos utilizado (Blog).
        template_name: El nombre de la plantilla a renderizar.
        context_object_name: El nombre de la variable de contexto para la lista de blogs.
        paginate_by: El número de elementos por página.
    """

    model = Blog    
    template_name = "search.html"
    context_object_name = "blogs"
    paginate_by = 9

    def get_queryset(self):
        """
        Obtiene la lista de blogs que coinciden con la consulta de búsqueda.

        Returns:
            QuerySet: Un conjunto de objetos Blog filtrados por la consulta.
        """
        query = self.request.GET.get("query", "")
        blogs = Blog.objects.filter(
            (Q(title__icontains=query) | Q(desc__icontains=query)), is_active=True
        ).order_by("-views")
        return blogs

    def get_context_data(self, **kwargs):
        """
        Obtiene el contexto para la plantilla, incluyendo la lista paginada de blogs y la consulta de búsqueda.

        Returns:
            dict: Un diccionario con el contexto para la plantilla.
        """
        context = super().get_context_data(**kwargs)
        paginator = Paginator(self.object_list, self.get_paginate_by(self.object_list))
        page = self.request.GET.get("page")

        try:
            blogs = paginator.page(page)
        except PageNotAnInteger:
            blogs = paginator.page(1)
        except EmptyPage:
            blogs = paginator.page(paginator.num_pages)

        context["blogs"] = blogs
        context["query"] = self.request.GET.get("query")
        return context

class CategoryView(View):
    """
    Vista para mostrar todas las categorías.

    Métodos:
        get: Renderiza la página de categorías con la lista de todas las categorías.
    """

    def get(self, request):
        """
        Maneja las solicitudes GET para la página de categorías.

        Args:
            request: El objeto de solicitud HTTP.

        Returns:
            HttpResponse: La respuesta HTTP con la página de categorías renderizada.
        """
        categories = Category.objects.all()
        return render(request, "category.html", {"categories": categories})

class GetCategory(View):
    """
    Vista para mostrar los blogs de una categoría específica.

    Métodos:
        get: Renderiza la página de una categoría específica.
    """

    def get(self, request, slug):
        """
        Maneja las solicitudes GET para la página de una categoría específica.

        Args:
            request: El objeto de solicitud HTTP.
            slug: El slug de la categoría.

        Returns:
            HttpResponse: La respuesta HTTP con la página de la categoría renderizada.
        """
        category = get_object_or_404(Category, slug=slug, is_active=True)
        return render(request, "get_category.html", {"category": category})

class TermsAndConditions(View):
    """
    Vista para la página de Términos y Condiciones.

    Métodos:
        get: Renderiza la página de Términos y Condiciones.
    """

    def get(self, request):
        """
        Maneja las solicitudes GET para la página de Términos y Condiciones.

        Args:
            request: El objeto de solicitud HTTP.

        Returns:
            HttpResponse: La respuesta HTTP con la página de Términos y Condiciones renderizada.
        """
        return render(request, "terms-and-conditions.html")

class BookmarkView(ListView):
    """
    Vista para mostrar los marcadores del usuario.

    Muestra una lista paginada de marcadores del usuario autenticado.

    Atributos:
        model: El modelo de datos utilizado (Bookmark).
        template_name: El nombre de la plantilla a renderizar.
        context_object_name: El nombre de la variable de contexto para la lista de marcadores.
        paginate_by: El número de elementos por página.
    """
    model = Bookmark
    template_name = 'bookmark.html'
    context_object_name = 'bookmarks'
    paginate_by = 9

    def get_queryset(self):
        """
        Obtiene la lista de marcadores del usuario autenticado.

        Returns:
            QuerySet: Un conjunto de objetos Bookmark del usuario autenticado.
        """
        if self.request.user.is_anonymous:
            messages.warning(request, "Auth required")
            return redirect("accounts:login")
        return Bookmark.objects.filter(creator=self.request.user).order_by("-created_on")

    def get_context_data(self, **kwargs):
        """
        Obtiene el contexto para la plantilla, incluyendo la lista paginada de marcadores.

        Returns:
            dict: Un diccionario con el contexto para la plantilla.
        """
        context = super().get_context_data(**kwargs)
        paginator = Paginator(self.object_list, self.get_paginate_by(self.object_list))
        page = self.request.GET.get("page")

        try:
            bookmarks = paginator.page(page)
        except PageNotAnInteger:
            bookmarks = paginator.page(1)
        except EmptyPage:
            bookmarks = paginator.page(paginator.num_pages)

        context["bookmarks"] = bookmarks
        return context
