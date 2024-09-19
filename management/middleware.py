from django.shortcuts import redirect
from django.contrib import messages

"""
Proposito:
Restringir el acceso a las rutas que comienzan con /manage/ a
usuarios autenticados y autorizados.

Comportamiento:
Si la ruta comienza con /manage/ y el usuario no esta autenticado o no tiene
el atributo is_author, se muestra un mensaje de advertencia y se redirige al
usuario a la página de inicio ( index ).
Si el usuario está autorizado, la solicitud se procesa normalmente.

"""


class ManagementAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/manage/'):
            if request.user.is_anonymous or not request.user.is_author:
                messages.warning(request, "Not authorized to access the page")
                return redirect("index")
        return self.get_response(request)
