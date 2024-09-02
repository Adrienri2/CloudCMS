from django.shortcuts import redirect, render
from django.views import View
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import User

class Login(View):
    """
    Vista para manejar el inicio de sesión de usuarios.

    Métodos:
        get: Renderiza la página de inicio de sesión.
        post: Autentica y inicia sesión al usuario.
    """

    def get(self, request):
        """
        Renderiza la página de inicio de sesión si el usuario no está autenticado.

        Args:
            request: El objeto de solicitud HTTP.

        Returns:
            HttpResponse: La respuesta HTTP con la página de inicio de sesión.
        """
        if request.user.is_authenticated:
            messages.info(request, "Ya has iniciado sesión, cierra sesión primero")
            return redirect("index")
        return render(request, "accounts/login.html")

    def post(self, request):
        """
        Autentica y inicia sesión al usuario.

        Args:
            request: El objeto de solicitud HTTP.

        Returns:
            HttpResponse: La respuesta HTTP con la página de inicio de sesión o redirige a la página principal.
        """
        uname = request.POST.get("username", "")
        passwd = request.POST.get("password", "")
        user = authenticate(username=uname, password=passwd)
        if user is not None:
            login(request, user)
            messages.success(request, "Iniciado sesión")
            return redirect("index")
        else:
            messages.warning(request, "El nombre de usuario o la contraseña son incorrectos")
        return render(request, "accounts/login.html")

@method_decorator(login_required, name="dispatch")
class Logout(View):
    """
    Vista para manejar el cierre de sesión de usuarios.

    Métodos:
        get: Cierra la sesión del usuario.
    """

    def get(self, request):
        """
        Cierra la sesión del usuario y redirige a la página de inicio de sesión.

        Args:
            request: El objeto de solicitud HTTP.

        Returns:
            HttpResponse: La respuesta HTTP que redirige a la página de inicio de sesión.
        """
        logout(request)
        messages.info(request, "Cerrado sesión")
        return redirect("accounts:login")

class Register(View):
    """
    Vista para manejar el registro de nuevos usuarios.

    Métodos:
        get: Renderiza la página de registro.
        post: Crea un nuevo usuario y lo autentica.
    """

    def get(self, request):
        """
        Renderiza la página de registro si el usuario no está autenticado.

        Args:
            request: El objeto de solicitud HTTP.

        Returns:
            HttpResponse: La respuesta HTTP con la página de registro.
        """
        if request.user.is_authenticated:
            messages.info(request, "Ya has iniciado sesión")
            return redirect("index")
        return render(request, "accounts/register.html")
    
    def post(self, request):
        """
        Crea un nuevo usuario y lo autentica.

        Args:
            request: El objeto de solicitud HTTP.

        Returns:
            HttpResponse: La respuesta HTTP que redirige a la página principal o de registro.
        """
        data = request.POST
        passwd1 = data.get("password1", "")
        passwd2 = data.get("password2","")
        if passwd1 and (passwd1 != passwd2):
            messages.warning(request, "Las contraseñas no coinciden")
            return redirect("accounts:register")
        
        email, username, firstname = data.get("email"), data.get("username"), data.get("firstname")
        if not (email and username and firstname):
            messages.info(request, "Se requiere correo electrónico, nombre de usuario y nombre")
            return redirect("accounts:register")
        
        user = User.objects.filter(Q(email=email) | Q(username=username))
        if not user.exists():
            user = User(email=email, username=username, first_name=firstname)
            if lastname := data.get("lastname"):
                user.last_name = lastname
            user.set_password(passwd1)
            user.save()
            messages.success(request, "Usuario creado")
            login(request, user)
            messages.success(request, "Iniciado sesión")
            return redirect("index")

        messages.info(request, "El usuario ya existe")
        return redirect("accounts:register")