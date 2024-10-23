
from .models import Category
from .models import Notification

def categories_processor(request):
    """
    Esta función es un contexto de procesador que se utiliza para añadir
    las categorías activas al contexto de todas las plantillas en la aplicación Django.

    Parámetros:
    request (HttpRequest): El objeto de solicitud HTTP.

    Retorna:
    dict: Un diccionario que contiene las categorías activas, que se añadirá
          al contexto de todas las plantillas.

    Funcionalidad:
    - Filtra las categorías para obtener solo aquellas que están activas (is_active=True).
    - Retorna un diccionario con las categorías activas.
    - Este diccionario se añadirá al contexto de todas las plantillas, lo que permite
      acceder a las categorías activas en cualquier plantilla sin necesidad de pasarlas
      explícitamente desde las vistas.
    """
    categories = Category.objects.filter(is_active=True)
    return {'categories': categories}


def notification_processor(request):
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(user=request.user, is_read=False)
        notifications_count = notifications.count()
        return {'notifications': notifications, 'notifications_count': notifications_count}
    return {}