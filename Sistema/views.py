from decimal import Decimal
from django.db.models import Sum
from datetime import date, timezone
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm , AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from .forms import TransaccionForm, CuentaContable, AsientoCustomForm
from .models import Asiento, Transaccion, PartidaDiaria
from .utils import filtrar_o_crear_partida_diaria
from .models import Empleado

def ingresar(request):
    if request.method == "GET":
        return render(request, "login.html", {"form": AuthenticationForm()})
    else:
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is None:
            return render(request, "login.html", {"form": AuthenticationForm(), "error": "Contraseña o usuario incorrecto."})
        else:
            login(request, user)
            return redirect("home")



def libro_diario(request):
    # Obtener todas las partidas diarias disponibles
    partidas_diarias = PartidaDiaria.objects.all()

    # Obtener la partida diaria de hoy por defecto
    hoy = date.today()
    partida_diaria_hoy = partidas_diarias.filter(fecha=hoy).first()

    # Si se selecciona una partida diaria específica
    partida_seleccionada = request.GET.get('partida_diaria', partida_diaria_hoy.id_partida_diaria if partida_diaria_hoy else None)
    transacciones = None
    if partida_seleccionada:
        transacciones = Transaccion.objects.filter(id_partida_diaria=partida_seleccionada)

    # Renderizar la página de inicio con la lista de partidas diarias y transacciones
    return render(request, 'libro_diario.html', {
        'partidas_diarias': partidas_diarias,
        'transacciones': transacciones,
        'partida_seleccionada': partida_seleccionada
    })

def home(request):
    return render(request, 'home.html', {"username":request.user.username})

def cerrarSesion(request):
    logout(request)
    return redirect("home")

def transaccion(request):
    if request.method == 'POST':
        formularioBase = TransaccionForm(request.POST)
        formularioAsientoContable = AsientoCustomForm(request.POST)

        if formularioBase.is_valid() and formularioAsientoContable.is_valid():
            # Guardar la transacción
            

            # Crear el asiento a partir de los datos del formulario
            cuenta_deudor = formularioAsientoContable.cleaned_data['cuenta_deudor']
            cuenta_acreedor = formularioAsientoContable.cleaned_data['cuenta_acreedor']
            monto = formularioAsientoContable.cleaned_data['monto']
        

            transaccion = formularioBase.save(commit=False)
            transaccion.total_debe = monto
            transaccion.total_haber = monto
            transaccion.id_partida_diaria = filtrar_o_crear_partida_diaria()

            transaccion.save()
            
            cuenta_acreedor.saldo_haber += monto
            cuenta_acreedor.save()

            cuenta_deudor.saldo_debe += monto
            cuenta_deudor.save()



            # Crear Asientos (uno para el Debe y otro para el Haber)
            Asiento.objects.create(
                id_transaccion=transaccion,
                id_cuenta=cuenta_deudor,
                monto_debe=monto,
                monto_haber=0,
            )

            Asiento.objects.create(
                id_transaccion=transaccion,
                id_cuenta=cuenta_acreedor,
                monto_debe=0,
                monto_haber=monto,
            )

            
            return redirect('home')  # Redirige a una página de éxito
        else:
            # Si hay errores, vuelve a renderizar el formulario con los errores
            params = {
                "transaccion_form": formularioBase,
                "asiento_formset": formularioAsientoContable,
                "readOnly": False,
                "error": "Hubo un error. Revisa los campos del formulario."
            }
            return render(request, 'transaccion.html', params)
    else:
        formularioBase = TransaccionForm()
        formularioAsientoContable = AsientoCustomForm()

    params = {
        "transaccion_form": formularioBase,
        "asiento_formset": formularioAsientoContable,
        "readOnly": False,
    }

    return render(request, 'transaccion.html', params)



def balance_comprobacion(request):
    # Obtener todas las cuentas contables
    cuentas = CuentaContable.objects.all()

    # Inicializar saldos totales como Decimal
    total_debe = Decimal('0.0')
    total_haber = Decimal('0.0')

    # Calcular los saldos de cada cuenta y asignar saldado_acreedor o saldado_deudor
    for cuenta in cuentas:
        # Calcular el saldo de la cuenta (Debe - Haber)
        saldo = cuenta.saldo_debe - cuenta.saldo_haber
        cuenta.saldo = saldo

        # Asignar el saldo correspondiente
        if saldo > 0:
            cuenta.saldado_deudor = saldo
            cuenta.saldado_acreedor = Decimal('0.0')
        else:
            cuenta.saldado_deudor = Decimal('0.0')
            cuenta.saldado_acreedor = abs(saldo)

        # Guardar la cuenta con el saldo actualizado
        cuenta.save()

        # Sumar al total de debe y haber
        total_debe += cuenta.saldo_debe
        total_haber += cuenta.saldo_haber

    # Renderizar la página de balance de comprobación
    return render(request, 'balance_comprobacion.html', {
        'cuentas': cuentas,
        'total_debe': total_debe,
        'total_haber': total_haber
    })


def mano_de_obra(request):
    empleados = Empleado.objects.all()  # Obtenemos todos los empleados
    empleado_seleccionado = None

    if request.method == 'POST':
        empleado_id = request.POST.get('empleado')
        if empleado_id:
            empleado_seleccionado = Empleado.objects.get(id_empleado=empleado_id)

    return render(request, 'mano_de_obra.html', {
        'empleados': empleados,
        'empleado_seleccionado': empleado_seleccionado
    })




def estado_de_resultados(request):
    return render(request, 'estado_de_resultados.html')

def libro_mayor(request):
    return render(request, 'libro_mayor.html')

def cierre_contable(request):
    return render(request, 'cierre_contable.html')





def handle_not_found(request, exception):
    return redirect('home')
