from django.urls import path
from . import views


app_name = 'accounts'
'''
Nombre de la aplicación para el espacio de nombres de URL.
'''

urlpatterns = [
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', views.Logout.as_view(), name='logout'),
    path('register/', views.Register.as_view(), name='register'),
    path('profile/', views.profile, name='profile')
]
'''
Lista de patrones de URL para la aplicación 'accounts'.
Cada entrada en la lista asocia una URL con una vista específica.
'''