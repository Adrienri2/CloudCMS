from django.conf import settings
from blogs.models import Category

"""
Este módulo define los procesadores de contexto para la aplicación de blogs.

Funciones:
- categories_processor(request): Devuelve un diccionario con las categorías activas.
- admin_media(request): Devuelve la configuración global de medios de administración.
"""

def categories_processor(request):
    """
    Devuelve un diccionario con las categorías activas.

    Parámetros:
    - request: La solicitud HTTP.

    Retorna:
    - Un diccionario con las categorías activas.
    """
    categories = list(Category.objects.filter(is_active=True).values('id', 'category', 'slug'))
    return {'categories': categories}

def admin_media(request):
    """
    Devuelve la configuración global de medios de administración.

    Parámetros:
    - request: La solicitud HTTP.

    Retorna:
    - La configuración global de medios de administración.
    """
    return settings.GLOBAL_SETTINGS