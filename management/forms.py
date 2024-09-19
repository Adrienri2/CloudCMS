from django import forms
from ckeditor.widgets import CKEditorWidget
from accounts.models import User 

class CKEditorForm(forms.Form):
    content = forms.CharField(widget = CKEditorWidget())

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "gender", "role"]
        labels = {
            "username": "Nombre de usuario",
            "email": "Correo electrónico",
            "first_name": "Nombre",
            "last_name": "Apellido",
            "gender": "Género",
            "role": "Rol"
        }
        widgets = {
            "role": forms.Select(choices=User.ROLE_CHOICES)
        }
