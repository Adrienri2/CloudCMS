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