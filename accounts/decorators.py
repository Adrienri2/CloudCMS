from django.core.exceptions import PermissionDenied
"""
Excepción que se lanza cuando un usuario no tiene permiso para realizar una acción.
"""
def role_required(allowed_roles):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                raise PermissionDenied
        return _wrapped_view
    return decorator

def permission_required_any(perms):
    """
    Decorador que verifica si el usuario tiene al menos uno de los permisos especificados.
    Args:
        perms (list): Lista de permisos a verificar.
        Returns:
        function: La vista decorada que solo se ejecutará si el usuario tiene al menos uno de los permisos.
    """
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            # Verifica si el usuario tiene al menos uno de los permisos especificados
            if not any(request.user.has_perm(perm) for perm in perms):
                # Si no tiene ninguno de los permisos, lanza una excepción de permiso denegado
                raise PermissionDenied
            # Si tiene al menos uno de los permisos, ejecuta la vista
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator