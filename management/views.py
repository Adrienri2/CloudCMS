from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views import View
from blogs.models import Category, Blog, Comment
from django.utils import timezone
from .forms import CKEditorForm
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import PermissionDenied
from accounts.decorators import role_required, permission_required_any 
# Importa el decorador desde accounts



# Create your views here.
class ManageBlog(View):
    def get(self, request):

        if request.user.role in ["editor", "admin", "publisher"]:
        # Si el usuario es un editor, admin o publicador, se muestran todos los blogs activos
            blogs = Blog.objects.filter(is_active=True)
        else:
        # Si el usuario es un autor, muestra solo sus blogs
            blogs = Blog.objects.filter(is_active=True, creator=request.user)

        # Añadir información adicional al contexto
        for blog in blogs:
            blog.can_edit_or_verify = blog.can_edit_or_verify(request.user)
            blog.button_text = blog.get_button_text(request.user)

        return render(request, "management/blog.html", {"blogs": blogs})

@method_decorator(role_required(['admin']), name='dispatch')
class ManageCategory(View):
    def get(self, request):
        categories = Category.objects.filter(is_active=True)
        return render(request, "management/category.html", {"categories": categories})


@method_decorator(permission_required('accounts.can_create_blog', raise_exception=True), name='dispatch')
#se verifica que el usuario cuente con el permiso de crear un blog
class CreateBlog(View):
    
    def get(self, request):
        form = CKEditorForm()
        categories = Category.objects.filter(is_active=True)
        return render(request, "management/create_blog.html", {"form": form, "categories": categories})

    def post(self, request):
        data = request.POST
        title = data.get("title")
        desc = data.get("desc")
        content = data.get("content")
        thumbnail = request.FILES.get("thumbnail")
        categories = data.getlist("categories") 
        status = data.get("status")

        if not (title, desc, content, thumbnail, categories, status):
            messages.info(request, "El título, la descripción, el contenido, la miniatura, las categorías o el estado no pueden estar vacíos")
            return redirect("manage:create_blog")

        try:
            status = int(status)
        except ValueError:
            messages.info(request, "Algo está mal con el estado")
            return redirect("manage:create_blog")
        

        is_published = status == 3 #si el estado es 3, entonces is_published es True, de lo contrario es False

        blog = Blog(
            title=title,
            desc=desc,
            content=content,
            creator=request.user,
            thumbnail=thumbnail,
            is_published=is_published,
            status=status
        )
        blog.save()
        for id in categories:
            try:
                c = Category.objects.get(id=int(id))
                blog.categories.add(c)
            except Exception as e:
                pass

        blog.save()
        messages.success(request, "Artículo creado")

        return redirect("manage:create_blog")

@method_decorator(role_required(['admin']), name='dispatch')
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


@method_decorator(permission_required_any(['accounts.can_edit_blog', 'accounts.can_publish_blog']), name='dispatch')
class EditBlog(View):
    def get(self, request, id):
        blog = Blog.objects.filter(id=id).first()
        if blog is None:
            # Si no se encuentra el blog, muestra un mensaje de información y redirige
            messages.info(request, "El artículo no existe")
            return redirect("manage:blog")
        
        # Obtiene todas las categorías disponibles
        categories = Category.objects.all()
        form = CKEditorForm({"content": blog.content})
        return render(request, "management/edit_blog.html", {"blog": blog, "categories": categories, "form": form})
    
    def post(self, request, id=None):
        # Obtiene los datos del formulario enviados en la solicitud POST
        data = request.POST
        id = data.get("id")
        
        blog = Blog.objects.filter(is_active=True, id=id).first()
        if blog is None:
            # Si no se encuentra el blog, muestra un mensaje de información y redirige
            messages.info(request, "El artículo no existe")
            return redirect("manage:blog")

        # Obtiene los datos del formulario
        title = data.get("title")
        desc = data.get("desc")
        content = data.get("content")
        status = data.get("status")
        thumbnail = request.FILES.get("thumbnail")
        categories = data.getlist("categories")
        status_comments = data.get("status_comments")

         # Verifica que el estado no sea None
        if not status:
            messages.warning(request, "Debe asignarle un estado")
            return redirect("manage:edit_blog", id=blog.id)
        
        # Actualiza los campos del blog
        blog.title = title
        blog.desc = desc
        blog.content = content
        if thumbnail:
            blog.thumbnail = thumbnail

        try:
            # Intenta convertir el estado a un entero y luego a un booleano
            status = int(status)
            blog.status = status
            # Publicado solo si el estado es 3
            blog.is_published = status == 3
            
            if blog.is_published:
                blog.published_on = timezone.now()
        except ValueError:
            # Si hay un error al convertir el estado, muestra un mensaje de información
            messages.info(request, "Error al actualizar el estado")
            return redirect("manage:edit_blog", id=blog.id)

        # Actualiza los comentarios del blog
        blog.status_comments = status_comments if status_comments else ""
        blog.last_modified_by = request.user
        blog.last_modified_by_role = request.user.role

        # Actualiza las categorías del blog
        blog.categories.set([])
        for id in categories:
            try:
                c = Category.objects.get(id=int(id))
                blog.categories.add(c)
            except Exception as e:
                pass

        # Guarda el blog con los cambios realizados
        blog.save()
        # Muestra un mensaje de éxito indicando que los cambios se han guardado
        messages.success(request, "Cambios guardados")

        # Redirige al usuario a la página de gestión de blogs
        return redirect("manage:blog")



#solo el admin y el autor pueden eliminar un blog
@method_decorator(permission_required('accounts.can_delete_blog', raise_exception=True), name='dispatch')
class DeleteBlog(View):
    def get(self, request, id):
        blog = Blog.objects.filter(id=id, creator=request.user).first()
        if blog is None:
            messages.warning(request, "El artículo no existe")
        else:
            blog.is_active = False
            blog.save()
            messages.info(request, "Artículo eliminado")

        return redirect("manage:blog")

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
    




class KanbanView(View):
    def get(self, request):
        user_role = request.user.role
        blogs_by_status = {}

        if user_role == 'author':
            blogs_by_status['Borrador'] = Blog.objects.filter(status=0, creator=request.user, is_active=True)
            blogs_by_status['En edición'] = Blog.objects.filter(status=1, creator=request.user, is_active=True)
            blogs_by_status['En espera'] = Blog.objects.filter(status=2, is_active=True, creator=request.user)
            blogs_by_status['Publicado'] = Blog.objects.filter(status=3, is_active=True, is_published=True, creator=request.user)
        elif user_role == 'editor':
            blogs_by_status['En edición'] = Blog.objects.filter(status=1, is_active=True)
            blogs_by_status['En espera'] = Blog.objects.filter(status=2, is_active=True)
        elif user_role == 'publisher':
            blogs_by_status['En espera'] = Blog.objects.filter(status=2, is_active=True)
            blogs_by_status['Publicado'] = Blog.objects.filter(status=3, is_active=True, is_published=True)
            
        else:
            user_role = 'admin'
            blogs_by_status['Borrador'] = Blog.objects.filter(status=0, is_active=True)
            blogs_by_status['En edición'] = Blog.objects.filter(status=1, is_active=True)
            blogs_by_status['En espera'] = Blog.objects.filter(status=2, is_active=True)
            blogs_by_status['Publicado'] = Blog.objects.filter(status=3, is_active=True, is_published=True)


        return render(request, "management/kanban.html", {"blogs_by_status": blogs_by_status})

class ManageComment(View):
    def get(self, request):
        comments = Comment.objects.filter(is_active=True, blog__in=Blog.objects.filter(creator=request.user))
        return render(request, "management/comment.html", {"comments": comments})

class DeleteComment(View):
    def get(self, request, id):
        comment = get_object_or_404(Comment.objects.filter(id=id, is_active=True))
        if comment.blog.creator.username != request.user.username:
            messages.warning(request, "No eres el autor de ese artículo")
            return redirect("manage:comment")
        comment.is_active = False
        comment.save()
        messages.success(request, "Comentario eliminado")
        return redirect("manage:comment")
    

