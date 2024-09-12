import os
import django
from django.conf import settings
from django.core.management import call_command

def check_static_files():
    # Configurar Django si no está configurado
    if not settings.configured:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cloudcms.settings')
        django.setup()

    ckeditor_path = os.path.join(settings.STATIC_ROOT, 'ckeditor')
    
    # Verificar la existencia del directorio CKEditor en STATIC_ROOT
    if not os.path.exists(ckeditor_path):
        print(f"ERROR: CKEditor directory not found at {ckeditor_path}")
        
        # Buscar el directorio ckeditor en STATICFILES_DIRS
        found = False
        for static_dir in settings.STATICFILES_DIRS:
            possible_path = os.path.join(static_dir, 'ckeditor')
            if os.path.exists(possible_path):
                print(f"Found CKEditor files in: {possible_path}")
                found = True
                break
        
        if not found:
            print("ERROR: CKEditor files not found in STATICFILES_DIRS")
    else:
        print("CKEditor directory found in STATIC_ROOT")
        
    # Verificar la instalación de CKEditor
    try:
        import ckeditor
        print(f"\nCKEditor installed at: {ckeditor.__file__}")
    except ImportError:
        print("\nERROR: CKEditor not installed or not in PYTHONPATH")
    
    # Verificar que los archivos estáticos estén correctamente recolectados
    try:
        call_command('collectstatic', interactive=False)
        print("\nStatic files collected successfully.")
    except Exception as e:
        print(f"\nERROR: Failed to collect static files: {e}")

if __name__ == "__main__":
    check_static_files()