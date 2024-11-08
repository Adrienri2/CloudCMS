import json
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.decorators import method_decorator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views import View
from django.db.models import F
from django.urls import reverse
from django.db.models import Q, Sum
from django.views.generic import TemplateView
from django.conf import settings
from accounts.models import DatosTarjeta
from django.utils.timezone import make_aware,localtime, is_naive
from datetime import datetime, timedelta
from django.utils import timezone
from .models import *
from .models import Notification, Category, FavoriteCategory, Blog, Rating
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
import openpyxl
from openpyxl.styles import Font, Alignment, Border, Side
from openpyxl.drawing.image import Image
from django.views.decorators.csrf import csrf_exempt
from PIL import Image as PILImage
import base64
from io import BytesIO
import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

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
      

        category = blog.category

        if category.subcategory_type == "paga":
            if request.user.is_authenticated:
                has_membership = PaidMembership.objects.filter(user=request.user, category=category).exists()
                if not has_membership:
                    return redirect('get_category', slug=category.slug)
            else:
                return redirect('get_category', slug=category.slug)

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
    """
    Vista para mostrar las notificaciones no leídas del usuario.

    Parámetros:
    request (HttpRequest): El objeto de solicitud HTTP.

    Retorna:
    HttpResponse: Renderiza la plantilla 'notifications.html' con las notificaciones no leídas
                  y el conteo de las mismas.

    Funcionalidad:
    - Filtra las notificaciones del usuario autenticado que no han sido leídas.
    - Ordena las notificaciones por fecha de creación en orden descendente.
    - Cuenta el número de notificaciones no leídas.
    - Renderiza la plantilla 'notifications.html' con las notificaciones y su conteo.
    """
    notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')
    notifications_count = notifications.count()
    return render(request, 'notifications.html', {'notifications': notifications, 'notifications_count': notifications_count})

@login_required
def mark_as_read(request, notification_id):
    """
    Vista para marcar una notificación específica como leída.

    Parámetros:
    request (HttpRequest): El objeto de solicitud HTTP.
    notification_id (int): El ID de la notificación a marcar como leída.

    Retorna:
    HttpResponseRedirect: Redirige a la vista 'manage:kanban'.

    Funcionalidad:
    - Obtiene la notificación especificada por ID y perteneciente al usuario autenticado.
    - Marca la notificación como leída.
    - Guarda los cambios en la base de datos.
    - Redirige a la vista 'manage:kanban'.
    """
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return redirect('manage:kanban')

@login_required
def mark_all_as_read(request):
    """
    Vista para marcar todas las notificaciones no leídas del usuario como leídas.

    Parámetros:
    request (HttpRequest): El objeto de solicitud HTTP.

    Retorna:
    HttpResponseRedirect: Redirige a la página anterior usando HTTP_REFERER.

    Funcionalidad:
    - Filtra las notificaciones no leídas del usuario autenticado.
    - Marca todas las notificaciones filtradas como leídas.
    - Redirige a la página anterior usando HTTP_REFERER.
    """
    notifications = Notification.objects.filter(user=request.user, is_read=False)
    notifications.update(is_read=True)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def toggle_favorite_category(request, category_id):
    """
    Vista para añadir o eliminar una categoría de las favoritas del usuario.

    Parámetros:
    request (HttpRequest): El objeto de solicitud HTTP.
    category_id (int): El ID de la categoría a añadir o eliminar de favoritas.

    Retorna:
    JsonResponse: Retorna un JSON con el estado de la operación ('added' o 'removed').

    Funcionalidad:
    - Obtiene la categoría especificada por ID.
    - Intenta obtener o crear una relación de categoría favorita para el usuario autenticado.
    - Si la relación ya existe, la elimina y retorna un estado 'removed'.
    - Si la relación no existe, la crea y retorna un estado 'added'.
    """
    category = get_object_or_404(Category, id=category_id)
    favorite, created = FavoriteCategory.objects.get_or_create(user=request.user, category=category)
    if not created:
        favorite.delete()
        return JsonResponse({'status': 'removed'})
    return JsonResponse({'status': 'added'})

@login_required
def favorite_categories(request):
    """
    Vista para mostrar las categorías favoritas del usuario.

    Parámetros:
    request (HttpRequest): El objeto de solicitud HTTP.

    Retorna:
    HttpResponse: Renderiza la plantilla 'blogs/favorite_categories.html' con las categorías favoritas.

    Funcionalidad:
    - Filtra las categorías favoritas del usuario autenticado.
    - Renderiza la plantilla 'blogs/favorite_categories.html' con las categorías favoritas.
    """
    favorites = FavoriteCategory.objects.filter(user=request.user)
    return render(request, 'blogs/favorite_categories.html', {'favorites': favorites})


class PagoView(View):
    def get(self, request, category_id ):
        category = get_object_or_404(Category, id=category_id)
        datos_tarjeta = None
        if hasattr(request.user, 'datos_tarjeta'):
            datos_tarjeta = {
                'nombre_tarjeta': request.user.datos_tarjeta.nombre_tarjeta,
                'numero_tarjeta': request.user.datos_tarjeta.numero_tarjeta,
                'fecha_vencimiento': request.user.datos_tarjeta.fecha_vencimiento,
                'codigo_seguridad': request.user.datos_tarjeta.codigo_seguridad,
            }
        return render(request, 'blogs/pago.html', {'category': category, 'datos_tarjeta': datos_tarjeta, 'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY})


class CreateCheckoutSessionView(View):
    def post(self, request, category_id, *args , **kwargs):
        category = get_object_or_404(Category, id=category_id)
        YOUR_DOMAIN = "http://127.0.0.1:8000/"
        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[
                {
                        'price_data': {
                            'currency': 'pyg',
                            'product_data': {
                                'name': category.category,
                                'description': category.desc,
                            },
                            'unit_amount': category.costo_membresia
                        },
                        'quantity': 1,
                    },
                ],
                mode='payment',
                success_url=YOUR_DOMAIN + reverse('blogs:success', kwargs={'category_id': category_id}),
                cancel_url=YOUR_DOMAIN + reverse('blogs:cancel', kwargs={'category_id': category_id}),
            )
            return redirect(checkout_session.url, code=303)
        except Exception as e:
            return str(e)
        

class SuccessView(View):
    def get(self, request, category_id):
        category = get_object_or_404(Category, id=category_id)
        return render(request, 'blogs/success.html', {'category': category})
    
class CancelView(View):
    def get(self, request, category_id):
        category = get_object_or_404(Category, id=category_id)
        return redirect('index')


@method_decorator(login_required, name='dispatch')
class IrACategoriaView(View):
    def get(self, request, category_id):
        category = get_object_or_404(Category, id=category_id)

         # Verificar si el usuario ya tiene una membresía para esta categoría
        if PaidMembership.objects.filter(user=request.user, category=category).exists():
            messages.success(request, "Ya tienes una membresía para esta categoría. Ve y disfruta de los Artículos.")
           
        else:
            # Guardar la membresía pagada
            PaidMembership.objects.create(
                user=request.user,
                category=category,
                category_desc=category.desc,
                category_type=category.category_type,
                subcategory_type=category.subcategory_type,
                membership_cost=category.costo_membresia
            )

            # Guardar el registro de pago de la membresía
            MembershipPayment.objects.create(
                user=request.user,
                category=category,
                category_type=category.category_type,
                membership_cost=category.costo_membresia
            )
            messages.success(request, "Tu membresía ha sido activada. Ahora puedes disfrutar de los Artículos.")

        # Redirigir a la pagina de la categoria
        return redirect('get_category', slug=category.slug)
    
    

@method_decorator(login_required, name='dispatch')
class MembershipsView(View):
    def get(self, request):
        query = request.GET.get('q')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        memberships = PaidMembership.objects.filter(user=request.user).order_by('-payment_date')

        if query:
            memberships = memberships.filter(
                Q(category__category__icontains=query) |
                Q(category_desc__icontains=query) |
                Q(category_type__iexact=query) |
                Q(membership_cost__icontains=query)
            )

        if start_date:
            start_date = make_aware(datetime.strptime(start_date, '%Y-%m-%d'))
        else:
            start_date = None

        if end_date:
            end_date = make_aware(datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)) - timedelta(microseconds=1)
            if start_date:
                memberships = memberships.filter(payment_date__range=[start_date, end_date])
            else:
                memberships = memberships.filter(payment_date__lte=end_date)
        elif start_date:
            memberships = memberships.filter(payment_date__gte=start_date)

        # Si no se encuentran pagos en el rango de fechas, ajustar start_date a la fecha del primer pago
        if not memberships.exists() and not start_date:
            first_payment = PaidMembership.objects.filter(user=request.user).order_by('payment_date').first()
            if first_payment:
                start_date = first_payment.payment_date
                memberships = PaidMembership.objects.filter(user=request.user, payment_date__gte=start_date)
 

        total_paid = memberships.aggregate(Sum('membership_cost'))['membership_cost__sum'] or 0

        return render(request, 'blogs/memberships.html', {'memberships': memberships, 'total_paid': total_paid})
    

    def post(self, request):
        membership_id = request.POST.get('membership_id')
        membership = get_object_or_404(PaidMembership, id=membership_id, user=request.user)
        
         # Eliminar el registro correspondiente en MembershipPayment
        MembershipPayment.objects.filter(user=request.user, category=membership.category).delete()
        
        # Eliminar la membresía
        membership.delete()

        # Recalcular el total pagado
        memberships = PaidMembership.objects.filter(user=request.user)
        total_paid = memberships.aggregate(Sum('membership_cost'))['membership_cost__sum'] or 0

        return redirect('blogs:memberships')
    

@method_decorator(login_required, name='dispatch')
class ExportMembershipsView(View):
    def get(self, request):
        query = request.GET.get('q')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        total_paid = request.GET.get('total_paid')
        memberships = PaidMembership.objects.filter(user=request.user).order_by('-payment_date')

        if query:
            memberships = memberships.filter(
                Q(category__category__icontains=query) |
                Q(category_desc__icontains=query) |
                Q(category_type__iexact=query) |
                Q(subcategory_type__iexact=query) |
                Q(membership_cost__icontains=query)
            )

        if start_date:
            start_date = make_aware(datetime.strptime(start_date, '%Y-%m-%d'))
            if end_date:
                end_date = make_aware(datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)) - timedelta(microseconds=1)
                memberships = memberships.filter(payment_date__range=[start_date, end_date])
            else:
                memberships = memberships.filter(payment_date__gte=start_date)

        # Crear el archivo Excel
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Membresías"

        # Establecer el título
        ws.merge_cells('A1:G1')
        title_cell = ws['A1']
        title_cell.value = "CLOUDCMS"
        title_cell.font = Font(size=20, bold=True)
        title_cell.alignment = Alignment(horizontal='center')
        
        # Información del usuario
        user_info = [
            ("Usuario:", request.user.username),
            ("Nombre:", request.user.get_full_name()),
            ("Correo:", request.user.email),
        ]

        row = 3
        for label, value in user_info:
            ws[f'A{row}'] = label
            ws[f'A{row}'].font = Font(bold=True)  # Aplicar negrita a las etiquetas
            ws[f'B{row}'] = value
            row += 1

         # Espacio entre la información del usuario y la tabla de membresías
        row += 1

        ws.append([])
        ws.append(["Membresías Pagadas en CloudCMS:"])
        ws['A' + str(ws.max_row)].font = Font(bold=True)
        ws.append([])

        # Escribir los encabezados
        headers = ["Nombre de la Categoría", "Descripción", "Tipo", "Subcategoría", "Costo (Gs.)","Tipo de Pago", "Fecha de Pago"]
        ws.append(headers)

        # Aplicar el estilo de negrita a los encabezados
        for cell in ws[ws.max_row]:
            cell.font = Font(bold=True)

       # Ajustar el ancho de las columnas
        column_widths = [25, 30, 15, 20, 10, 15, 20]
        for i, width in enumerate(column_widths, 1):
            ws.column_dimensions[openpyxl.utils.get_column_letter(i)].width = width
 
        
        # Definir el estilo de borde
        thin_border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )

        # Aplicar el estilo de borde a los encabezados
        for cell in ws[ws.max_row]:
            cell.border = thin_border


        # Escribir los datos
        for membership in memberships:
            row = [
                membership.category.category,
                membership.category_desc,
                membership.category_type,
                membership.subcategory_type,
                membership.membership_cost,
                "TC/TD",
                membership.payment_date.strftime("%d %b, %Y %H:%M:%S")
            ]
            ws.append(row)
            for cell in ws[ws.max_row]:
                cell.border = thin_border


        # Escribir el total pagado
        ws.append([])
        ws.append(["Total General Pagado:", f"Gs. {total_paid}"])
        for cell in ws[ws.max_row]:
            cell.border = thin_border

        # Preparar la respuesta HTTP
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        filename = f"Membresias_{request.user.username}.xlsx"
        response['Content-Disposition'] = f'attachment; filename={filename}'
        wb.save(response)
        return response

def filter_payments(query, start_date, end_date):
    payments = MembershipPayment.objects.all().order_by('-payment_date')
    
    if query:
        payments = payments.filter(
            Q(user__username__icontains=query) |
            Q(category__category__icontains=query) |
            Q(category_type__iexact=query) |
            Q(membership_cost__icontains=query)
        )

    if start_date:
        start_date = make_aware(datetime.strptime(start_date, '%Y-%m-%d'))
    else:
        start_date = None

    if end_date:
        end_date = make_aware(datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)) - timedelta(microseconds=1)
        if start_date:
            payments = payments.filter(payment_date__range=[start_date, end_date])
        else:
            payments = payments.filter(payment_date__lte=end_date)
    elif start_date:
        payments = payments.filter(payment_date__gte=start_date)

    # Si no se encuentran pagos en el rango de fechas, ajustar start_date a la fecha del primer pago
    if not payments.exists() and not start_date:
        first_payment = MembershipPayment.objects.order_by('payment_date').first()
        if first_payment:
            start_date = first_payment.payment_date
            payments = MembershipPayment.objects.filter(payment_date__gte=start_date)

    return payments

@method_decorator(permission_required('accounts.can_view_membership_payments', raise_exception=True), name='dispatch')
class AllMembershipPaymentsView(View):
    def get(self, request):
        query = request.GET.get('q')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        payments = filter_payments(query, start_date, end_date)
        
        total_paid = payments.aggregate(Sum('membership_cost'))['membership_cost__sum'] or 0

        return render(request, 'blogs/all_membership_payments.html', {'payments': payments, 'total_paid': total_paid})
    
    def post(self, request):
        payment_id = request.POST.get('payment_id')
        payment = get_object_or_404(MembershipPayment, id=payment_id)
        
        # Eliminar el registro correspondiente en PaidMembership
        PaidMembership.objects.filter(user=payment.user, category=payment.category).delete()
        
        # Eliminar el registro en MembershipPayment
        payment.delete()

        # Recalcular el total pagado
        payments = MembershipPayment.objects.all()
        total_paid = payments.aggregate(Sum('membership_cost'))['membership_cost__sum'] or 0
        
        
        return redirect('blogs:all_membership_payments')
    

@method_decorator(login_required, name='dispatch')
class StatisticsView(TemplateView):
    template_name = 'blogs/estadisticas.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener los parámetros de filtro desde el request
        query = self.request.GET.get('q')
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        
        # Aplicar el filtro en los pagos
        payments = filter_payments(query, start_date, end_date)

        # Obtener los datos de las categorías y los totales comprados por cada categoría
        categories = payments.values('category__category').annotate(total=Sum('membership_cost')).order_by('-total')

        # Preparar los datos para el gráfico de pie
        labels = [category['category__category'] for category in categories]
        data = [category['total'] for category in categories]

        # Obtener los pagos agrupados por fecha
        payments_by_date = payments.values('payment_date__date').annotate(total=Sum('membership_cost')).order_by('payment_date__date')

        # Preparar los datos para el gráfico de barra/linea de tiempo
        dates = [payment['payment_date__date'].strftime("%Y-%m-%d") for payment in payments_by_date]
        totals = [payment['total'] for payment in payments_by_date]

        # Obtener los pagos agrupados por fecha y categoría
        payments_by_date_and_category = payments.values('payment_date__date', 'category__category').annotate(total=Sum('membership_cost')).order_by('payment_date__date')

        # Preparar los datos para el gráfico de línea de tiempo por categoría
        category_data = {}
        for payment in payments_by_date_and_category:
            category = payment['category__category']
            date = payment['payment_date__date'].strftime("%Y-%m-%d")
            total = payment['total']
            if category not in category_data:
                category_data[category] = []
            category_data[category].append({'x': date, 'y': total})

        # Pasar los datos al contexto
        context['labels'] = json.dumps(labels)
        context['data'] = json.dumps(data)
        context['dates'] = json.dumps(dates)
        context['totals'] = json.dumps(totals)
        context['category_data'] = json.dumps(category_data)
        
        return context

@method_decorator(login_required, name='dispatch')
class ExportStatisticsView(View):
    def post(self, request):
        # Obtener los datos de los gráficos desde el formulario
        pie_chart = request.POST.get('pie_chart')
        bar_chart = request.POST.get('bar_chart')
        line_chart = request.POST.get('line_chart')


        # Crear un nuevo libro de trabajo
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Análisis General de Membresías"

        # Establecer el título
        ws.merge_cells('A1:G1')
        title_cell = ws['A1']
        title_cell.value = "CLOUDCMS"
        title_cell.font = Font(size=20, bold=True)
        title_cell.alignment = Alignment(horizontal='center')

        # Espacio entre el título y la tabla de membresías
        ws.append([])
        ws.append(["Todas las Membresías Pagadas en CloudCMS:"])
        ws['A' + str(ws.max_row)].font = Font(bold=True)
        ws.append([])

        # Escribir los encabezados
        headers = ["Usuario", "Nombre de la Categoría", "Tipo", "Costo (Gs.)", "Tipo de Pago", "Fecha de Pago"]
        ws.append(headers)

        # Aplicar el estilo de negrita a los encabezados
        for cell in ws[ws.max_row]:
            cell.font = Font(bold=True)

        # Ajustar el ancho de las columnas
        column_widths = [25, 30, 15, 20, 15, 20]
        for i, width in enumerate(column_widths, 1):
            ws.column_dimensions[openpyxl.utils.get_column_letter(i)].width = width

        # Definir el estilo de borde
        thin_border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )

        # Aplicar el estilo de borde a los encabezados
        for cell in ws[ws.max_row]:
            cell.border = thin_border

        # Escribir los datos de todas las membresías pagadas
        payments = MembershipPayment.objects.all().order_by('-payment_date')
        for payment in payments:
            payment_date = payment.payment_date
            if is_naive(payment_date):
                payment_date = make_aware(payment_date)
            row = [
                payment.user.username,
                payment.category.category,
                payment.category_type,
                f"Gs. {payment.membership_cost}",
                "TC/TD",  # Asumiendo que el tipo de pago es siempre TC/TD
                localtime(payment.payment_date).strftime("%d %b, %Y %H:%M:%S")
            ]
            ws.append(row)
            for cell in ws[ws.max_row]:
                cell.border = thin_border

         # Calcular el total pagado
        total_paid = payments.aggregate(Sum('membership_cost'))['membership_cost__sum'] or 0

         # Escribir el total pagado
        ws.append([])
        ws.append(["Total General Pagado:", f"Gs. {total_paid}"])
        for cell in ws[ws.max_row]:
            cell.border = thin_border
        


        # Añadir los gráficos al archivo Excel
        if pie_chart:
            pie_image = self.base64_to_image(pie_chart)
            ws.add_image(pie_image, 'I3')
            

        if bar_chart:
            bar_image = self.base64_to_image(bar_chart)
            ws.add_image(bar_image, 'I40')
            

        if line_chart:
            line_image = self.base64_to_image(line_chart)
            ws.add_image(line_image, 'I70')
            

        # Preparar la respuesta HTTP
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=estadisticas_membresias.xlsx'
        wb.save(response)
        return response

    def base64_to_image(self, base64_string):
        image_data = base64.b64decode(base64_string.split(',')[1])
        image = PILImage.open(BytesIO(image_data))
        image_io = BytesIO()
        image.save(image_io, format='PNG')
        image_io.seek(0)
        return Image(image_io)
    

class RateBlogView(View):
    def post(self, request, blog_id):
        blog = get_object_or_404(Blog, id=blog_id)
        rating_value = int(request.POST.get('rating'))
        user = request.user

        # Obtener la calificación existente del usuario si existe
        rating, created = Rating.objects.get_or_create(user=user, blog=blog, defaults={'rating': rating_value})

        # Descontar la calificación anterior
        if not created:
            if rating.rating == 1:
                blog.one_star_ratings -= 1
            elif rating.rating == 2:
                blog.two_star_ratings -= 1
            elif rating.rating == 3:
                blog.three_star_ratings -= 1

        # Actualizar la calificación con la nueva
        rating.rating = rating_value
        rating.save()

        # Incrementar la nueva calificación
        if rating_value == 1:
            blog.one_star_ratings += 1
        elif rating_value == 2:
            blog.two_star_ratings += 1
        elif rating_value == 3:
            blog.three_star_ratings += 1

        blog.save()
        return redirect('manage:blog_detail', id=blog.id)
    


class ReportBlogView(View):
    def post(self, request, id):
        blog = get_object_or_404(Blog, id=id)
        report_reason = request.POST.get('report_reason')
        Report.objects.create(blog=blog, user=request.user, reason=report_reason)
        return redirect('blogs:blog', slug=blog.slug)
    

class ReportedBlogsView(View):
    def get(self, request):
        reports = Report.objects.all().order_by('-created_at')
        return render(request, 'blogs/blogs_reportados.html', {'reports': reports})
    


class VerificarReporteView(View):
    def get(self, request, id):
        report = get_object_or_404(Report, id=id)
        blog = report.blog
        return render(request, 'blogs/verificar_blog_reportado.html', {'blog': blog, 'report': report})


class ChangeBlogStatusView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, blog_id):
        try:
            print(f"Request received for blog_id: {blog_id}")
            blog = Blog.objects.get(id=blog_id)
            data = json.loads(request.body)  # Cargar el cuerpo de la solicitud como JSON
            new_status = data.get('new_status')  # Obtener new_status del JSON
            previous_status = data.get('previous_status')  # Obtener estado previo del JSON
            Comment = None 

            print(f"Data received: new_status={new_status}, previous_status={previous_status}")

            if new_status is None:
                print("new_status es None")
                return JsonResponse({'success': False, 'error': 'new_status es None'})

            new_status = int(new_status)

            if new_status == 2:  # Estado "En edición"
                blog.previous_status = blog.status  # Guardar el estado anterior
                blog.status = new_status
                blog.is_published = False  # Establecer is_published a False
                
                blog.save()

                # Eliminar todos los reportes del blog
                Report.objects.filter(blog=blog).delete()
                print("Blog status updated and reports deleted successfully")
                
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


class IgnorarReporteView(View):
    def get(self, request, id):
        report = get_object_or_404(Report, id=id)
        report.delete()
        return redirect('blogs:blogs_reportados')