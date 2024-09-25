from django.shortcuts import redirect, render
from django.views import View
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from accounts.models import User
from .decorators import role_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from management.forms import UserForm 
from django.contrib.auth.models import Permission
from django.contrib.auth.decorators import permission_required

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
        
        email, username, firstname, gender= data.get("email"), data.get("username"), data.get("firstname"), data.get("gender")
        if not (email and username and firstname and gender):
            messages.info(request, "Se requiere correo electrónico, nombre de usuario, género y nombre")
            return redirect("accounts:register")
        
        user = User.objects.filter(Q(email=email) | Q(username=username))
        if not user.exists():
            user = User(email=email, username=username, first_name=firstname, gender=gender, role='suscriptor')
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
    
@login_required
def profile(request):
    """
    Vista para mostrar el perfil del usuario.
    """
    return render(request, 'accounts/profile.html')


@method_decorator(permission_required('accounts.can_view_user', raise_exception=True), name='dispatch')
class UserListView(View):
    """
    Vista para listar todos los usuarios.
    """

    def get(self, request):
        """
        Renderiza la página con la lista de usuarios.

        Args:
            request: El objeto de solicitud HTTP.

        Returns:
            HttpResponse: La respuesta HTTP con la página de lista de usuarios.
        """
        users = User.objects.all()
        return render(request, 'accounts/user_list.html', {'users': users})


@method_decorator(permission_required('accounts.can_edit_user', raise_exception=True), name='dispatch')
class EditUserView(View):
    """
    Vista para editar un usuario.
    """

    def get(self, request, user_id):
        """
        Renderiza la página de edición de usuario.

        Args:
            request: El objeto de solicitud HTTP.
            user_id: El ID del usuario a editar.

        Returns:
            HttpResponse: La respuesta HTTP con la página de edición de usuario.
        """
        user = get_object_or_404(User, id=user_id)
        form = UserForm(instance=user)
        # Obtener los permisos asignados al usuario
        assigned_permissions = user.user_permissions.all()
        return render(request, 'management/edit_user.html', {
            'form': form, 
            'user': user, 
            'assigned_permissions': assigned_permissions
            })

    def post(self, request, user_id):
        """
        Maneja la solicitud POST para editar un usuario.

        Args:
            request: El objeto de solicitud HTTP.
            user_id: El ID del usuario a editar.

        Returns:
            HttpResponseRedirect: Redirige a la página de lista de usuarios después de editar.
        """
        user = get_object_or_404(User, id=user_id)
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            user.save(update_permissions=False)  # No actualizar permisos automáticamente
            form.save_m2m() # Guardar los permisos seleccionados
            selected_permissions = form.cleaned_data.get('permissions')
            print("Permisos seleccionados:", [perm.name for perm in selected_permissions])

            # Asignar los permisos seleccionados al usuario
            user.user_permissions.set(selected_permissions)
            user.save()

            # Obtener los permisos asignados al usuario después de guardar
            assigned_permissions = user.user_permissions.all()
            print("Permisos asignados después de guardar:", [perm.name for perm in assigned_permissions])

            messages.success(request, 'Cambios guardados con éxito')  
            return HttpResponseRedirect(reverse('management:users'))
        else:
            print("Errores del formulario:", form.errors)
            print("Datos del formulario:", form.cleaned_data)

        # Obtener los permisos asignados al usuario en caso de error en el formulario
        assigned_permissions = user.user_permissions.all()
        return render(request, 'management/edit_user.html', {
            'form': form,
            'user': user,
            'assigned_permissions': assigned_permissions,
        })
        


    