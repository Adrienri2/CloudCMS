from celery import shared_task
from django.utils import timezone
from .models import Blog

@shared_task
def publish_scheduled_blogs():
    now = timezone.now()
    blogs_to_publish = Blog.objects.filter(status=2, scheduled_date__lte=now)
    for blog in blogs_to_publish:
        blog.status = 3
        blog.is_published = True
        blog.published_on = now
        blog.scheduled_date = None
        blog.save()