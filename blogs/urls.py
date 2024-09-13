"""
Este módulo define las rutas URL para la aplicación de blogs.

Rutas:

- create/comment/: Crea un comentario en un blog. Requiere autenticación.
- create/reply/: Crea una respuesta a un comentario. Requiere autenticación.
- create/bookmark/: Crea un marcador para un blog. Requiere autenticación.
- create/like/: Crea un like en un blog. Requiere autenticación.
- <slug:slug>/: Muestra una entrada de blog específica basada en el slug.
"""

from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views


app_name = "blogs"

urlpatterns = [
    path("create/comment/", login_required(views.CreateComment.as_view()), name="create_comment"),
    path("create/reply/", login_required(views.CreateReply.as_view()), name="create_reply"),
    path("create/bookmark/", login_required(views.CreateBookmark.as_view()), name="create_bookmark"),
    path("create/like/", login_required(views.CreateLike.as_view()), name="create_like"),
    path("<slug:slug>/", views.BlogView.as_view(), name="blog"),
]