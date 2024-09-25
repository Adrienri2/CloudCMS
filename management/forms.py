from django import forms
from django.contrib.auth.models import Permission
from ckeditor.widgets import CKEditorWidget
from accounts.models import User 

class CKEditorForm(forms.Form):
    content = forms.CharField(widget = CKEditorWidget())

class UserForm(forms.ModelForm):
    
    # Definir los permisos específicos que deseas mostrar
    specific_permissions = [
        "can_assign_permissions",
        "can_create_category",
        "can_edit_category",
        "can_delete_category",
        "can_create_blog",
        "can_view_blog",
        "can_publish_blog",
        "can_edit_blog",
        "can_delete_blog",
    ]

    permissions = forms.ModelMultipleChoiceField(queryset=Permission.objects.filter(codename__in=specific_permissions), widget=forms.SelectMultiple, required=False, label="Permisos")
    
    
    
    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "gender", "role", "permissions"]
        labels = {
            "username": "Nombre de usuario",
            "email": "Correo electrónico",
            "first_name": "Nombre",
            "last_name": "Apellido",
            "gender": "Género",
            "role": "Rol",
            "permissions": "Permisos"
        }
        widgets = {
            "role": forms.Select(choices=User.ROLE_CHOICES)
        }
