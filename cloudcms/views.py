from urllib import request
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.db.models import Q
from django.views.generic import ListView
from blogs.models import Blog, Bookmark, Category
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages

class Index(View):
    def get(self, request):
        if request.user.is_authenticated:
            # Si el usuario está autenticado, mostrar todos los blogs
            blog_list = Blog.objects.filter(is_active=True, is_published=True).order_by("-published_on") 
        else:
            # Si el usuario no está autenticado, mostrar solo los blogs de categorías públicas
            public_categories = Category.objects.filter(subcategory_type='publica')
            blog_list = Blog.objects.filter(is_active=True, is_published=True, category__in=public_categories).order_by("-published_on")
    

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
    model = Blog
    template_name = "search.html"
    context_object_name = "blogs"
    paginate_by = 9

    def get_queryset(self):
        query = self.request.GET.get("query", "")
        blogs = Blog.objects.filter(
            (Q(title__icontains=query) | Q(desc__icontains=query)), is_active=True
        ).order_by("-published_on")
        return blogs

    def get_context_data(self, **kwargs):
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
    def get(self, request):
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
        category = get_object_or_404(Category, slug=slug)
        costo_membresia = category.costo_membresia if category else None
        return render(request, 'get_category.html', {
            'category': category,  # Pasar la categoría al contexto
            'costo_membresia': costo_membresia,  # Pasar el costo de la membresía al contexto
        })

class TermsAndConditions(View):
    def get(self, request):
        return render(request, "terms-and-conditions.html")

class BookmarkView(ListView):
    model = Bookmark
    template_name = 'bookmark.html'
    context_object_name = 'bookmarks'
    paginate_by = 9

    def get_queryset(self):
        if self.request.user.is_anonymous:
            messages.warning(request, "Auth required")
            return redirect("accounts:login")
        return Bookmark.objects.filter(creator=self.request.user).order_by("-created_on")

    def get_context_data(self, **kwargs):
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
