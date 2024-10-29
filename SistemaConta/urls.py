from django.urls import path
from . import views

app_name = 'SistemaConta'

urlpatterns = [
    #arreglar el inicio
    path('', views.prueba_view, name='prueba'),
    path('index/', views.index_view, name='index'),
    path('comprobaciones/', views.pantallaComprobacion_view, name='comprobaciones'),
    path('transaccion/', views.transaccion_view, name='transaccion'),
    path('manoObra/', views.manoObra_view, name='manoObra'),
    path('estados/', views.pantallaEstados_view, name='estados'),
    path('catalogo/', views.pantallaCatalogo_view, name='catalogo'),
]

