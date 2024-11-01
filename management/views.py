import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views import View
from blogs.models import BlogVersion, Category, Blog, Comment
from django.utils import timezone
from .forms import CKEditorForm
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import PermissionDenied
from accounts.decorators import role_required, permission_required_any 
import pytz
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
from blogs.tasks import publish_scheduled_blogs, expire_scheduled_blogs  #Importar las tareas de Celery


# Importa el decorador desde accounts


# Create your views here.

# Configurar el logger
logger = logging.getLogger(__name__)

# Crear una versión del blog
def create_blog_version(blog, user):
    version= BlogVersion.objects.create(
        blog=blog,
        title=blog.title,
        desc=blog.desc,
        content=blog.content,
        thumbnail=blog.thumbnail,
        category=blog.category,
        modified_by=user,
        modified_by_role=user.role
    )
    logger.debug(f"Versión creada para el blog '{blog.title}' con ID {blog.id} por el usuario '{user.username}' con rol '{user.role}'")


# Vista para listar las versiones del blog
def blog_versions(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)
    versions = BlogVersion.objects.filter(blog=blog).order_by('-created_at')
    return render(request, 'management/blog_versions.html', {'blog': blog, 'versions': versions})


# Vista para mostrar una versión específica del blog
def blog_version_preview(request, version_id):
    version = get_object_or_404(BlogVersion, id=version_id)
    return render(request, 'management/blog_version.html', {'version': version})


class GetBlogStatusView(View):
    def get(self, request, blog_id):
        try:
            blog = Blog.objects.get(id=blog_id)
            return JsonResponse({'previous_status': blog.previous_status, 'return_comment': blog.status_comments})
        except Blog.DoesNotExist:
            return JsonResponse({'previous_status': None, 'return_comment': ''})


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
        category_id = request.POST.get('category') 
        category = get_object_or_404(Category, id=category_id)

        if not (title, desc, content, thumbnail, category_id):
            messages.info(request, "El título, la descripción, el contenido, la miniatura, las categorías no pueden estar vacíos")
            return redirect("manage:create_blog")
        
        is_published = False  # El estado inicial es "Borrador", por lo tanto, no está publicado


        blog = Blog(
            title=title,
            desc=desc,
            content=content,
            creator=request.user,
            thumbnail=thumbnail,
            is_published=is_published,
            status=0,  # Asignar el estado 0 (Borrador) automáticamente
            category=category,
            is_active=True
        )
        blog.save()

        # Asignar el slug como el id del blog
        blog.slug = blog.id
        blog.save()

        # Crear y guardar una versión del blog
        blog_version = BlogVersion(
            blog=blog,
            title=blog.title,
            desc=blog.desc,
            content=blog.content,
            thumbnail=blog.thumbnail,
            category=blog.category,
            modified_by=request.user,  # Asignar el usuario que creó la versión
            modified_by_role=request.user.role  # Asignar el rol del usuario que creó la versión
        )
        blog_version.save()

        messages.success(request, "Artículo creado")
        return redirect("manage:blog")
   

@method_decorator(role_required(['admin']), name='dispatch')
class CreateCategory(View):
    def get(self, request):
        return render(request, "management/create_category.html")

    def post(self, request):
        data = request.POST
        category = data.get("category")
        desc = data.get("desc")
        category_type = data.get("category_type")
        subcategory_type = data.get("subcategory_type")
        costo_membresia = request.POST.get('costo_membresia')

        if not category:
            messages.warning(request, "El nombre de la categoría no puede estar vacío")
            return redirect("manage:create_category")

        c = Category.objects.filter(category=category, is_active=True).first()
        if c is not None:
            messages.warning(request, "La categoría ya existe")
        else:
            c = Category(
                category=category,
                desc=desc,
                category_type=category_type,
                subcategory_type=subcategory_type,
                costo_membresia=costo_membresia,
            
            )
            c.save()
            messages.success(request, "Categoría creada")
        return redirect("manage:category")


@method_decorator(permission_required_any(['accounts.can_edit_blog', 'accounts.can_publish_blog', 'accounts.can_create_blog']), name='dispatch')
class EditBlog(View):
    def get(self, request, id):
        blog = Blog.objects.filter(id=id).first()
        if blog is None:
            # Si no se encuentra el blog, muestra un mensaje de información y redirige
            messages.info(request, "El artículo no existe")
            return redirect("manage:blog")
        
        # Verificar permiso 'can_create_blog' y estado 'Borrador'
        if request.user.has_perm('accounts.can_create_blog') and not request.user.has_perm('accounts.can_edit_blog') and not request.user.has_perm('accounts.can_publish_blog') and blog.status != 0:
            raise PermissionDenied
        
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
        category_id = data.get("category")
        scheduled_date = data.get("scheduled_date")  # Obtener la fecha programada
        expiry_date = data.get("expiry_date")  # Obtener la fecha de caducidad



        # Verifica que el estado no sea None
        if request.user.has_perm('accounts.can_publish_blog')  and not status:
            messages.warning(request, "Debe asignarle un estado")
            return redirect("manage:edit_blog", id=blog.id)
        

        
        
        # Actualiza los campos del blog
        blog.title = title
        blog.desc = desc
        blog.content = content
        if thumbnail:
            blog.thumbnail = thumbnail

        try:
             # Ajustar el estado del blog según los permisos del usuario
            if request.user.has_perm('accounts.can_create_blog'):
                blog.status = 0  # Borrador
            elif request.user.has_perm('accounts.can_edit_blog'):
                blog.status = 1  # En edición
            elif request.user.has_perm('accounts.can_publish_blog'):
                # Intenta convertir el estado a un entero y luego a un booleano
                status = int(status)
                blog.status = status
                # Publicado solo si el estado es 3
                blog.is_published = status == 3
                
                if blog.is_published:
                    blog.published_on = timezone.now()
                elif status == 2 and scheduled_date:  # Manejar la programación de la publicación
                
                    # Convertir la fecha y hora ingresada a un objeto datetime
                    local_scheduled_date = timezone.datetime.strptime(scheduled_date, '%Y-%m-%dT%H:%M')
                    
                    # Asegurarse de que el objeto datetime tenga información de zona horaria
                    local_scheduled_date = timezone.make_aware(local_scheduled_date, timezone.get_current_timezone())
                    
                    # Convertir la fecha y hora local a UTC
                    utc_scheduled_date = local_scheduled_date.astimezone(pytz.UTC)
                    
                    if utc_scheduled_date > timezone.now():
                        blog.scheduled_date = utc_scheduled_date
                    else:
                        messages.warning(request, "La fecha y hora programadas deben estar en el futuro.")
                        return redirect("manage:edit_blog", id=blog.id)
                else:
                    blog.scheduled_date = None

                # Manejar la fecha de caducidad
                if expiry_date:
                    local_expiry_date = timezone.datetime.strptime(expiry_date, '%Y-%m-%dT%H:%M')
                    local_expiry_date = timezone.make_aware(local_expiry_date, timezone.get_current_timezone())
                    utc_expiry_date = local_expiry_date.astimezone(pytz.UTC)
                    
                    if utc_expiry_date > timezone.now():

                        blog.expiry_date = utc_expiry_date
                    else:
                        messages.warning(request, "La fecha y hora de caducidad deben estar en el futuro.")
                        return redirect("manage:edit_blog", id=blog.id)
                else:
                    blog.expiry_date = None


        except ValueError:
            # Si hay un error al convertir el estado, muestra un mensaje de información
            messages.info(request, "Error al actualizar el estado")
            return redirect("manage:edit_blog", id=blog.id)

        # Actualiza el ultimo usuario que modificó el blog
        blog.last_modified_by = request.user
        blog.last_modified_by_role = request.user.role

        # Actualiza las categorías del blog
        category = get_object_or_404(Category, id=category_id)
        blog.category = category

         # Verifica que el category_id no sea None y que la categoría exista
        if category_id:
            category = get_object_or_404(Category, id=category_id)
            blog.category = category
        else:
            messages.warning(request, "Debe asignarle una categoría")
            return redirect("manage:edit_blog", id=blog.id)
        


        # Guarda el blog con los cambios realizados
        blog.save()

        # Obtener la última versión del blog
        last_version = BlogVersion.objects.filter(blog=blog).order_by('-created_at').first()

        # Comparar el contenido del blog actual con la última versión
        if not last_version or (
            blog.title != last_version.title or
            blog.desc != last_version.desc or
            blog.content != last_version.content or
            blog.thumbnail != last_version.thumbnail or
            blog.category != last_version.category
        ):
            # Si hay cambios, se formatea blog.status_comments para que sea None
            blog.status_comments=None
            blog.save()
            print("AL MODIFICAR EL BLOG, SE FORMATEA EL COMENTARIO DE DEVOLUCIÓN")  # Mensaje de depuración

            # Si hay cambios, crear una nueva versión del blog
            BlogVersion.objects.create(
                blog=blog,
                title=blog.title,
                desc=blog.desc,
                content=blog.content,
                thumbnail=blog.thumbnail,
                category=blog.category,
                modified_by=request.user,
                modified_by_role=request.user.role,
                return_comment= blog.status_comments
            )
            print("AL MODIFICAR EL BLOG, SE CREA UNA NUEVA VERSION")  # Mensaje de depuración

        # Muestra un mensaje de éxito indicando que los cambios se han guardado
        messages.success(request, "Cambios guardados")

        # Redirige al usuario a la página de gestión de blogs
        return redirect("manage:blog")



@permission_required('accounts.can_publish_blog', raise_exception=True)
def schedule_publication(request, blog_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        scheduled_date = data.get('scheduled_date') # Obtener la fecha programada
        expiry_date = data.get('expiry_date')  # Obtener la fecha de caducidad
        
        blog = get_object_or_404(Blog, id=blog_id)

        try:
            # Convertir la fecha y hora ingresada a un objeto datetime
            local_scheduled_date = timezone.datetime.strptime(scheduled_date, '%Y-%m-%dT%H:%M')
            # Asegurarse de que el objeto datetime tenga información de zona horaria
            local_scheduled_date = timezone.make_aware(local_scheduled_date, timezone.get_current_timezone())
            # Convertir la fecha y hora local a UTC
            utc_scheduled_date = local_scheduled_date.astimezone(pytz.UTC)
            
            # Convertir la fecha de caducidad a un objeto datetime
            local_expiry_date = timezone.datetime.strptime(expiry_date, '%Y-%m-%dT%H:%M')
            local_expiry_date = timezone.make_aware(local_expiry_date, timezone.get_current_timezone())
            utc_expiry_date = local_expiry_date.astimezone(pytz.UTC)
            

            if utc_scheduled_date > timezone.now() and utc_expiry_date > utc_scheduled_date:
                blog.scheduled_date = utc_scheduled_date # Guardar la fecha programada
                blog.expiry_date = utc_expiry_date  # Guardar la fecha de caducidad
                blog.status = 2  # En espera
                blog.save()
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'error': 'La fecha y hora programadas deben estar en el futuro y la fecha de caducidad debe ser posterior a la fecha de publicación.'})
        except ValueError:
            return JsonResponse({'success': False, 'error': 'Error al procesar las fecha y horas ingresadas.'})
    return JsonResponse({'success': False, 'error': 'Método no permitido.'})


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
        category_type = data.get("category_type")
        subcategory_type = data.get("subcategory_type")
        nuevo_costo_membresia = data.get("nuevo_costo_membresia")

        
        if not (category and desc and category_type and subcategory_type and c):
            messages.warning(request, "No se pueden dejar los campos vacíos. O la categoría no existe")
            return redirect("manage:category")
        c.category = category
        c.desc = desc
        c.category_type = category_type
        c.subcategory_type = subcategory_type

        if nuevo_costo_membresia:
            try:
                nuevo_costo_membresia = float(nuevo_costo_membresia)
                c.costo_membresia = nuevo_costo_membresia
                print(f"Nuevo costo de la Membresía: {nuevo_costo_membresia}")  # Mensaje de depuración
            except ValueError:
                messages.error(request, "El costo de la membresía debe ser un número válido.")
                return redirect("manage:edit_category", id=id)


        c.save()
        messages.success(request, "Cambios guardados")
        return redirect("manage:category")

        

class DeleteCategory(View):
    def get(self, request, id):
        category = get_object_or_404(Category, id=id)
        print("Categoría eliminada:", category.id)  # Mensaje de depuración
        category.delete()
        messages.info(request, "Categoría eliminada")
        return redirect("manage:category")
    




class KanbanView(View):
    def get(self, request):
        user_role = request.user.role
        category_type = request.GET.get('category_type', 'moderada') # Por defecto 'moderada'

        blogs_by_status = {}

        
        # Filtrar categorías según el tipo de categoría seleccionado
        categories = Category.objects.filter(category_type=category_type) if category_type else Category.objects.all()

        # Filtrar blogs según el rol del usuario y la categoría seleccionada
        if user_role == 'author':
            if category_type == 'moderada':
                blogs_by_status['Borrador'] = Blog.objects.filter(status=0, creator=request.user, is_active=True, category__category_type=category_type)
                blogs_by_status['En edición'] = Blog.objects.filter(status=1, creator=request.user, is_active=True, category__category_type=category_type)
                blogs_by_status['En espera'] = Blog.objects.filter(status=2, is_active=True, creator=request.user, category__category_type=category_type)
                blogs_by_status['Publicado'] = Blog.objects.filter(status=3, is_active=True, is_published=True, creator=request.user, category__category_type=category_type)
            else:
                blogs_by_status['Borrador'] = Blog.objects.filter(status=0, creator=request.user, is_active=True, category__category_type=category_type)
                blogs_by_status['Publicado'] = Blog.objects.filter(status=3, is_active=True, is_published=True, creator=request.user, category__category_type=category_type)
            
        elif user_role == 'editor':
            blogs_by_status['Borrador'] = Blog.objects.filter(status=0, is_active=True, category__category_type=category_type)
            blogs_by_status['En edición'] = Blog.objects.filter(status=1, is_active=True, category__category_type=category_type)
            blogs_by_status['En espera'] = Blog.objects.filter(status=2, is_active=True, category__category_type=category_type)
            blogs_by_status['Publicado'] = Blog.objects.filter(status=3, is_active=True, is_published=True, category__category_type=category_type)
        elif user_role == 'publisher':
            if category_type == 'moderada':
                blogs_by_status['Borrador'] = Blog.objects.filter(status=0, is_active=True, category__category_type=category_type)
                blogs_by_status['En edición'] = Blog.objects.filter(status=1, is_active=True, category__category_type=category_type)
                blogs_by_status['En espera'] = Blog.objects.filter(status=2, is_active=True, category__category_type=category_type)
                blogs_by_status['Publicado'] = Blog.objects.filter(status=3, is_active=True, is_published=True, category__category_type=category_type)
            else:
                blogs_by_status['Borrador'] = Blog.objects.filter(status=0, is_active=True, category__category_type=category_type)
                blogs_by_status['Publicado'] = Blog.objects.filter(status=3, is_active=True, is_published=True, category__category_type=category_type)
        else:
            if category_type == 'moderada':
                user_role = 'admin'
                blogs_by_status['Borrador'] = Blog.objects.filter(status=0, is_active=True, category__category_type=category_type)
                blogs_by_status['En edición'] = Blog.objects.filter(status=1, is_active=True, category__category_type=category_type)
                blogs_by_status['En espera'] = Blog.objects.filter(status=2, is_active=True, category__category_type=category_type)
                blogs_by_status['Publicado'] = Blog.objects.filter(status=3, is_active=True, is_published=True, category__category_type=category_type)
            else:
                blogs_by_status['Borrador'] = Blog.objects.filter(status=0, is_active=True, category__category_type=category_type)
                blogs_by_status['Publicado'] = Blog.objects.filter(status=3, is_active=True, is_published=True, category__category_type=category_type)
            


        return render(request, "management/kanban.html", {
            "blogs_by_status": blogs_by_status,
            "categories": categories,
            "category_type": category_type,
            })

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
    

class ChangeBlogStatusView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, blog_id):
        try:
            blog = Blog.objects.get(id=blog_id)
            data = json.loads(request.body)  # Cargar el cuerpo de la solicitud como JSON
            new_status = data.get('new_status')  # Obtener new_status del JSON
            comment = data.get('comment')  # Obtener el comentario del JSON
            previous_status = data.get('previous_status')  # Obtener estado previo del JSON

            if new_status is None:
                print("new_status es None")
                return JsonResponse({'success': False, 'error': 'new_status es None'})

            new_status = int(new_status)

            if new_status in [0, 1, 2, 3]:
                blog.previous_status = blog.status  # Guardar el estado anterior
                blog.status = new_status
                blog.is_published = new_status == 3  # Actualizar is_published
                if blog.is_published:
                    blog.published_on = timezone.now()  # Actualizar la fecha de publicación

                if comment:  # Guardar comentario de justificación
                    formatted_date = timezone.now().strftime('%Y-%m-%d %H:%M')  # Formatear la fecha
                    blog.status_comments = f"{comment}\n\t | Devolución realizada por: {request.user.username}, Rol: {request.user.role}, Fecha: {formatted_date}"
                
                blog.save()

                # Verificar si el blog está avanzando en el flujo de aprobación
                if blog.previous_status is not None and blog.previous_status < blog.status:
                    # Obtener la última versión del blog
                    last_version = BlogVersion.objects.filter(blog=blog).order_by('-created_at').first()

                    # Comparar el contenido del blog actual con la última versión
                    if not last_version or (
                        blog.title != last_version.title or
                        blog.desc != last_version.desc or
                        blog.content != last_version.content or
                        blog.thumbnail != last_version.thumbnail or
                        blog.category != last_version.category
                    ):
                        # Si hay cambios, crear una nueva versión del blog
                        # Crear una versión del blog
                        BlogVersion.objects.create(
                            blog=blog,
                            title=blog.title,
                            desc=blog.desc,
                            content=blog.content,
                            thumbnail=blog.thumbnail,
                            category=blog.category,
                            modified_by=request.user,
                            modified_by_role=request.user.role
                        )
                        print("VERSION CREADA PUNTO 1. Hubo cambios")  # Mensaje de depuración
                    else:
                        # Si no hay cambios, eliminar el comentario return_comment
                        new_version = BlogVersion.objects.create(
                            blog=blog,
                            title=blog.title,
                            desc=blog.desc,
                            content=blog.content,
                            thumbnail=blog.thumbnail,
                            category=blog.category,
                            modified_by=request.user,
                            modified_by_role=request.user.role,
                            return_comment= None
                        )
                        print("VERSION CREADA PUNTO 2")  # Mensaje de depuración
                        # Comparar la nueva versión con la versión anterior
                        print("Si no hay cambios, eliminar el comentario return_comment")  # Mensaje de depuración
                        # Comparar la nueva versión con la versión anterior
                        
                        if last_version and (
                            new_version.title == last_version.title and
                            new_version.desc == last_version.desc and
                            new_version.content == last_version.content and
                            new_version.thumbnail == last_version.thumbnail and
                            new_version.category == last_version.category and
                            new_version.return_comment == last_version.return_comment
                        ):
                            print("Se creó una nueva version")  # Mensaje de depuración
                            # Si son idénticas, eliminar la nueva versión
                            new_version.delete()
                            print("Nueva versión eliminada, identica a la anterior ")  # Mensaje de depuración
                else:
                        # Crear una versión del blog al retroceder en el flujo
                        print("SE RETROCEDE EN EL FLUJO ")  # Mensaje de depuración
                        BlogVersion.objects.create(
                            blog=blog,
                            title=blog.title,
                            desc=blog.desc,
                            content=blog.content,
                            thumbnail=blog.thumbnail,
                            category=blog.category,
                            modified_by=request.user,
                            modified_by_role=request.user.role,
                            return_comment=blog.status_comments if blog.previous_status > blog.status else None  # Guardar el comentario de devolución
                        )
                        print("Se creó una nueva versión ")  # Mensaje de depuración


                return JsonResponse({'success': True})
            else:
                print(f"Estado no válido: {new_status}")
                return JsonResponse({'success': False, 'error': 'Estado no válido.'})
        except Blog.DoesNotExist:
            print(f"Blog no encontrado: {blog_id}")
            return JsonResponse({'success': False, 'error': 'Blog no encontrado.'})
        except Exception as e:
            print(f"Error al cambiar el estado del blog: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)})

class BlogPreviewView(View):
    def get(self, request, blog_id):
        blog = get_object_or_404(Blog, id=blog_id)
        last_version = BlogVersion.objects.filter(blog=blog).order_by('-created_at').first()
        return render(request, 'management/blog_preview.html', {'blog': blog, 'last_version': last_version})
    

class RevertToVersionView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request):
        try:
            print("RevertToVersionView POST request received")  # Mensaje de depuración
            data = json.loads(request.body)
            print(f"Data received: {data}")  # Mensaje de depuración

            blog_id = data.get('blog_id')
            version_id = data.get('version_id')

            if not blog_id or not version_id:
                print("Faltan blog_id o version_id")  # Mensaje de depuración
                return JsonResponse({'success': False, 'error': 'Faltan blog_id o version_id'})

            print(f"Blog ID: {blog_id}, Version ID: {version_id}")  # Mensaje de depuración


            blog = get_object_or_404(Blog, id=blog_id)
            version = get_object_or_404(BlogVersion, id=version_id)

            print(f"Blog encontrado: {blog.title}, Versión encontrada: {version.title}")  # Mensaje de depuración


            # Crear una nueva versión idéntica a la versión en cuestión
            new_version = BlogVersion.objects.create(
                blog=blog,
                title=version.title,
                desc=version.desc,
                content=version.content,
                thumbnail=version.thumbnail,
                category=version.category,
                modified_by=request.user,
                modified_by_role=request.user.role,
                return_comment=None
            )

            print(f"Nueva versión creada: {new_version.id}")  # Mensaje de depuración


            # Actualizar el contenido del modelo Blog
            blog.title = version.title
            blog.desc = version.desc
            blog.content = version.content
            blog.thumbnail = version.thumbnail
            blog.category = version.category
            blog.status_comments = None  # Eliminar comentario de devolución
            blog.save()

            print(f"Blog actualizado: {blog.title}")  # Mensaje de depuración


            return JsonResponse({'success': True})
        except Exception as e:
            print(f"Error al revertir a la versión :c: {str(e)}")  # Mensaje de depuración
            return JsonResponse({'success': False, 'error': str(e)})


@method_decorator(role_required(['admin']), name='dispatch')
class SetFeaturedBlogView(View):
    def post(self, request, blog_id):
        try:
            blog = get_object_or_404(Blog, id=blog_id, is_published=True, is_active=True)
            blog.is_featured = not blog.is_featured  # Alternar el estado de destacado
            if blog.is_featured:
                blog.featured_at = timezone.now()  # Establecer la fecha y hora actual
            else:
                blog.featured_at = None  # Eliminar la fecha y hora si se quita de destacados
            blog.save()
            return JsonResponse({'success': True, 'is_featured': blog.is_featured})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
        


class BlogDetailView(View):
    def get(self, request, id):
        blog = get_object_or_404(Blog, id=id)
        return render(request, 'blogs/blog.html', {'blog': blog})