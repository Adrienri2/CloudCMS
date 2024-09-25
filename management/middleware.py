from django.shortcuts import redirect
from django.contrib import messages

"""
Proposito:
Restringir el acceso a las rutas que comienzan con /manage/ a
usuarios autenticados y autorizados.

Comportamiento:
Si la ruta comienza con /manage/ y el usuario no esta autenticado o tiene
el rol de "suscriptor", se muestra un mensaje de advertencia y se redirige al
usuario a la página de inicio ( index ).
Si el usuario está autorizado, la solicitud se procesa normalmente.

"""


class ManagementAuthMiddleware:
    def __init__(self, get_response):
        # Guarda la referencia a la siguiente capa del middleware o la vista
       
        self.get_response = get_response

    def __call__(self, request):
        # Verifica si la ruta de la solicitud comienza con /manage/
        if request.path.startswith('/manage/'):
            # Verifica si el usuario no está autenticado o tiene el rol de "suscriptor"
            if request.user.is_anonymous or request.user.role == "suscriptor":
                # Muestra un mensaje de advertencia y redirige al usuario a la página de inicio
                messages.warning(request, "Not authorized to access the page")
                return redirect("index")
            
        # Si el usuario está autorizado, procesa la solicitud normalmente    
        return self.get_response(request)
