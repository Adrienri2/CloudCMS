from django.urls import path
from . import views

app_name = "manage"

urlpatterns = [
    path("category/", views.ManageCategory.as_view(), name="category"),

    path("delete/category/<int:id>", views.DeleteCategory.as_view(), name="delete_category"),

    path("edit/category/<int:id>", views.EditCategory.as_view(), name="edit_category"),
]
