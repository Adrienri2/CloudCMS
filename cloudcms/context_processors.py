from django.conf import settings
from blogs.models import Category

def categories_processor(request):
    categories = list(Category.objects.filter(is_active=True).values('id', 'category', 'slug'))
    return {'categories': categories}

def admin_media(request):
    return settings.GLOBAL_SETTINGS
