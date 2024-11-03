"""
URL configuration for SistemaContableAutomatizado project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from Sistema import views as SistemaViews
from django.conf.urls import handler404


urlpatterns = [
    # Funciones sistema
    path('admin/', admin.site.urls, name="adminPanel"),  # URL para el panel de administración
    path('', SistemaViews.home, name='start'),  # Start
    path('home/', SistemaViews.home, name='home'),  # URL para el inicio de sesión
    path('libro_diario/', SistemaViews.libro_diario, name='libro_diario'),  # URL para el libro diario
    path('login/', SistemaViews.ingresar, name='login'),  # URL para el inicio de sesión
    path('logout/', SistemaViews.cerrarSesion, name='logout'),  # URL para cerrar sesión y redireccionar al inicio
    # Funciones herramienta
    path('transaccion/', SistemaViews.transaccion, name='transaccion'),
    path('balance_comprobacion/', SistemaViews.balance_comprobacion, name='balance_comprobacion'),
    path('mano_de_obra/', SistemaViews.mano_de_obra, name='mano_de_obra'),
    path('estados_financieros/', SistemaViews.estados_financieros, name='estados_financieros'),
    path('libro_mayor/', SistemaViews.libro_mayor, name='libro_mayor'),
    path('cierre_contable/', SistemaViews.cierre_contable, name='cierre_contable'),
    # Estados Financieros
    path('estado_de_capital/', SistemaViews.estado_de_capital, name='estado_de_capital'),
    path('estado_de_resultados/', SistemaViews.estado_de_resultados, name='estado_de_resultados'),
    path('balance_general/', SistemaViews.balance_general, name='balance_general'),

]

handler404 = 'Sistema.views.handle_not_found'
