from django.urls import path
from . import views

app_name = 'SistemaConta'

urlpatterns = [
    #arreglar el inicio
    path('', views.prueba_view, name='index'),
    path('index/', views.index_view, name='index'),
    path('prueba/', views.prueba_view, name='prueba'),
]

