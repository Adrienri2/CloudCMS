from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views import View
from blogs.models import Category, Blog, Comment
from django.utils import timezone
from .forms import CKEditorForm


class ManageCategory(View):
    def get(self, request):
        categories = Category.objects.filter(is_active=True)
        return render(request, "management/category.html", {"categories": categories})


class CreateCategory(View):
    def get(self, request):
        return render(request, "management/create_category.html")

    def post(self, request):
        data = request.POST
        category = data.get("category")
        desc = data.get("desc")

        c = Category.objects.filter(category=category).first()
        if c is not None:
            messages.warning(request, "La categoría ya existe")
        else:
            c = Category(
                category=category,
                desc=desc
            )
            c.save()
            messages.success(request, "Categoría creada")
        return redirect("manage:create_category")

class EditCategory(View):
    def get(self, request, id):
        category = get_object_or_404(Category, id=id, is_active=True)
        return render(request, "management/edit_category.html", {"category": category})

    def post(self, request, id):
        c = Category.objects.filter(id=id, is_active=True).first()
        data = request.POST
        category, desc = data.get("category"), data.get("desc")
        if not ((category and desc) or c):
            messages.warning(request, "La categoría o la descripción no pueden estar vacías. O la categoría no existe")
            return redirect("manage:category")
        c.category = category
        c.desc = desc
        c.save()
        messages.success(request, "Cambios guardados")
        return redirect("manage:category")
        

class DeleteCategory(View):
    def get(self, request, id):
        category = get_object_or_404(Category, id=id)
        category.is_active = False
        category.save()
        messages.info(request, "Categoría eliminada")
        return redirect("manage:category")
