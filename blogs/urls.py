from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views

app_name = "blogs"

urlpatterns = [
    path("create/comment/", login_required(views.CreateComment.as_view()), name="create_comment"),
    path("<slug:slug>/", views.BlogView.as_view(), name="blog"),
]
