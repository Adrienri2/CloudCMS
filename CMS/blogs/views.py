from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views import View
from django.db.models import F
from django.urls import reverse
from .models import *

# Create your views here.
def get_blog_url(slug):
    return reverse("blogs:blog", args=[slug])

class CreateComment(View):
    def post(self, request):
        blog = get_object_or_404(Blog.objects.filter(is_active=True, id=request.POST.get("id")))
        comment = request.POST.get("comment")
        if not comment:
            messages.warning(request, "Comment required")
            return redirect("blogs:blog", slug=blog.slug)
        c = Comment(
            comment = comment,
            creator = request.user,
            blog = blog
        )
        c.save()
        messages.success(request, "Comment created")
        return redirect(get_blog_url(blog.slug)+"#comments")

