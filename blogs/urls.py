"""
Este módulo define las rutas URL para la aplicación de blogs.

Rutas:

- create/comment/: Crea un comentario en un blog. Requiere autenticación.
- create/reply/: Crea una respuesta a un comentario. Requiere autenticación.
- create/bookmark/: Crea un marcador para un blog. Requiere autenticación.
- create/like/: Crea un like en un blog. Requiere autenticación.
- <slug:slug>/: Muestra una entrada de blog específica basada en el slug.
"""

from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views
from .views import notifications, mark_as_read, mark_all_as_read, toggle_favorite_category, favorite_categories


app_name = "blogs"

urlpatterns = [
    path("create/comment/", login_required(views.CreateComment.as_view()), name="create_comment"),
    path("create/reply/", login_required(views.CreateReply.as_view()), name="create_reply"),
    path("create/bookmark/", login_required(views.CreateBookmark.as_view()), name="create_bookmark"),
    path('pago/<int:category_id>/', views.PagoView.as_view(), name='pago'),
    path('procesar_pago/<int:category_id>/', views.ProcesarPagoView.as_view(), name='procesar_pago'),
    path('success/<int:category_id>/', views.SuccessView.as_view(), name='success'),  # Vista de éxito
    path('memberships/', views.MembershipsView.as_view(), name='memberships'),  # Vista de membresías
    path('delete_membership/<int:membership_id>/', views.DeleteMembershipView.as_view(), name='delete_membership'),  # Vista para eliminar membresías
    path('all_membership_payments/', views.AllMembershipPaymentsView.as_view(), name='all_membership_payments'),  # Vista para ver todas las membresías pagadas
    path("create/like/", login_required(views.CreateLike.as_view()), name="create_like"),
    path("<slug:slug>/", views.BlogView.as_view(), name="blog"),
    path('notifications/', notifications, name='notifications'),
    path('notifications/mark_as_read/<int:notification_id>/', mark_as_read, name='mark_as_read'),
    path('notifications/mark_all_as_read/', mark_all_as_read, name='mark_all_as_read'),
    path('toggle_favorite_category/<int:category_id>/', toggle_favorite_category, name='toggle_favorite_category'),
    path('favorite_categories/', favorite_categories, name='favorite_categories'),




]