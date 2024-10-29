from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
#from .models import //Aqui van los modelos a importar # importamos el modelo Usuario de la aplicacion SistemaConta 
from django.contrib.auth.decorators import login_required 

# Create your views here.

#Index es el archivo LOGIN de la pagina
def index_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            return render(request, 'index.html', {'error': 'Usuario o contraseña incorrectos'})
    else:
        return render(request, 'index.html')

@login_required
def prueba_view(request):
    return render(request, 'Inicio.html')
@login_required
def pantallaComprobacion_view(request):
    return render(request, 'pantalla_comprobacion.html')
@login_required
def pantallaEstados_view(request):
    return render(request, 'pantalla_estados.html')
@login_required
def pantallaCatalogo_view(request):
    return render(request, 'pantalla_catalogo.html')