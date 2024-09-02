"""
Configuración de URL para el proyecto cloudcms.

La lista `urlpatterns` enruta las URLs a las vistas. Para más información, consulta:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Ejemplos:
Vistas basadas en funciones
    1. Añade una importación:  from my_app import views
    2. Añade una URL a urlpatterns:  path('', views.home, name='home')
Vistas basadas en clases
    1. Añade una importación:  from other_app.views import Home
    2. Añade una URL a urlpatterns:  path('', Home.as_view(), name='home')
Incluyendo otra configuración de URL
    1. Importa la función include(): from django.urls import include, path
    2. Añade una URL a urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Incluir URLs de las aplicaciones
    path("accounts/", include("accounts.urls")),
    path("manage/", include("management.urls")),

    # Vistas principales
    path("", views.Index.as_view(), name="index"),
    path("trendings/", views.Trendings.as_view(), name="trendings"),
    path("latest/", views.Latest.as_view(), name="latest"),
    path("popular/", views.Popular.as_view(), name="popular"),
    path("search/", views.Search.as_view(), name="search"),
    path("bookmark/", views.BookmarkView.as_view(), name="bookmark"),
    path("terms-and-conditions/", views.TermsAndConditions.as_view(), name="terms_and_conditions"),
    path("category/", views.CategoryView.as_view(), name="category"),
    path("category/<slug:cat>/", views.GetCategory.as_view(), name="get_category"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Añadir URLs estáticas
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)