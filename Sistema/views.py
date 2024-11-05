from django.http import HttpResponseRedirect
from django.urls import reverse
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
from .models import Asiento, Transaccion, PartidaDiaria, CuentaContable, BalanceGeneral, CuentasBalanceGeneral
from .utils import filtrar_o_crear_partida_diaria
from .models import Empleado
from .forms import EmpleadoForm 
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
        'transacciones': transacciones.order_by('-fecha_operacion', '-id_transaccion'),
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
def saldar(cuenta):
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


def saldar_cuentas():
    # Obtener todas las cuentas contables
    cuentas = CuentaContable.objects.all()

    # Iterar sobre cada cuenta y saldarla
    for cuenta in cuentas:
        saldar(cuenta)

    print("Todas las cuentas han sido saldadas.")


def balance_comprobacion(request):
    # Salda todas las cuentas antes de mostrar el balance de comprobación
    saldar_cuentas()




def balance_comprobacion(request):
    # Obtener todas las cuentas contables
    cuentas = CuentaContable.objects.all()

    # Inicializar saldos totales como Decimal
    total_debe = Decimal('0.0')
    total_haber = Decimal('0.0')

    # Sumar al total de debe y haber con las cuentas actualizadas
    for cuenta in cuentas:
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
    if request.method == 'POST':
        # Capturar datos del formulario
        nombre = request.POST.get('nombre')
        salario_nominal_diario = request.POST.get('salario_nominal_diario')
        dias_semanales = request.POST.get('dias_semanales')

        # Convertir datos a tipos numéricos adecuados
        salario_nominal_diario = Decimal(salario_nominal_diario)
        dias_semanales = int(dias_semanales)

        # Crear un nuevo empleado y guardar en la base de datos
        nuevo_empleado = Empleado(
            nombre=nombre,
            salario_nominal_diario=salario_nominal_diario,
            dias_semanales=dias_semanales
        )
        nuevo_empleado.save()  # Se llama a `calcular_costos` antes de guardar, si está configurado en el modelo

        # Redirigir para evitar reenvío del formulario en la recarga
        return redirect('mano_de_obra')  # Cambia 'mano_de_obra' por el nombre correcto de la URL

    # Obtener todos los empleados y calcular los totales
    empleados = Empleado.objects.all()
    total_salario_nominal_diario = sum(emp.salario_nominal_diario for emp in empleados)
    total_septimo = sum(emp.septimo for emp in empleados)
    total_vacaciones = sum(emp.vacaciones for emp in empleados)
    total_aguinaldo = sum(emp.aguinaldo for emp in empleados)
    total_isss = sum(emp.isss for emp in empleados)
    total_afp = sum(emp.afp for emp in empleados)
    total_incaf = sum(emp.incaf for emp in empleados)
    total_costo_real_semanal = sum(emp.costo_real_semanal for emp in empleados)

    context = {
        'empleados': empleados,
        'total_salario_nominal_diario': total_salario_nominal_diario,
        'total_septimo': total_septimo,
        'total_vacaciones': total_vacaciones,
        'total_aguinaldo': total_aguinaldo,
        'total_isss': total_isss,
        'total_afp': total_afp,
        'total_incaf': total_incaf,
        'total_costo_real_semanal': total_costo_real_semanal,
    }

    return render(request, 'mano_de_obra.html', context)

def libro_mayor(request):
    # Obtener todas las partidas diarias disponibles
    partidas_diarias = PartidaDiaria.objects.all()

    # Obtener todas las transacciones ordenadas por fecha, de más recientes a más antiguas
    transacciones = Transaccion.objects.all().order_by('-fecha_operacion', '-id_transaccion')

    # Renderizar la página de inicio con la lista de partidas diarias y transacciones
    return render(request, 'libro_mayor.html', {
        'partidas_diarias': partidas_diarias,
        'transacciones': transacciones,
    })


def cierre_contable(request):
    return render(request, 'cierre_contable.html')

def handle_not_found(request, exception):
    return redirect('home')


def estados_financieros(request):
    return render(request, 'estados_financieros.html')

def estado_de_capital(request):
    return render(request, 'estado_de_capital.html')
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


def saldar_cuentas():
    # Obtener todas las cuentas contables
    cuentas = CuentaContable.objects.all()

    # Iterar sobre cada cuenta y saldarla
    for cuenta in cuentas:
        saldar(cuenta)

    print("Todas las cuentas han sido saldadas.")

def generar_balance_general():
    # Se llena la fecha
    fecha_actual = date.today()
    
    # Se saldan todas las cuentas
    saldar_cuentas()

    # Filtrar todas las cuentas de activos, pasivos y patrimonio desde CuentaContable
    cuentas_activos = CuentaContable.objects.filter(categoria='Activos')
    cuentas_pasivos = CuentaContable.objects.filter(categoria='Pasivos')
    cuentas_patrimonio = CuentaContable.objects.filter(categoria='Patrimonio')

    # Calcular activos_debe, activos_haber y activos_saldo
    activos_debe = sum([cuenta.saldado_deudor for cuenta in cuentas_activos])
    activos_haber = sum([cuenta.saldado_acreedor for cuenta in cuentas_activos])
    activos_saldo = activos_debe - activos_haber

    if activos_saldo > 0:
        activos_debe = activos_saldo
        activos_haber = Decimal('0.0')
    else:
        activos_debe = Decimal('0.0')
        activos_haber = abs(activos_saldo)

    
    print(f"Activos - Debe: {activos_debe}, Haber: {activos_haber}, Saldo: {activos_saldo}")

    # Calcular pasivos_debe, pasivos_haber y pasivos_saldo
    pasivos_debe = sum([cuenta.saldado_deudor for cuenta in cuentas_pasivos])
    pasivos_haber = sum([cuenta.saldado_acreedor for cuenta in cuentas_pasivos])
    pasivos_saldo = pasivos_haber - pasivos_debe
    print(f"Pasivos - Debe: {pasivos_debe}, Haber: {pasivos_haber}, Saldo: {pasivos_saldo}")
    
    if pasivos_saldo > 0:
        pasivos_debe = Decimal('0.0')
        pasivos_haber = pasivos_saldo
    else:
        pasivos_debe = abs(pasivos_saldo)
        pasivos_haber = Decimal('0.0')

    # Calcular patrimonio_debe, patrimonio_haber y patrimonio_saldo
    patrimonio_debe = sum([cuenta.saldado_deudor for cuenta in cuentas_patrimonio])
    patrimonio_haber = sum([cuenta.saldado_acreedor for cuenta in cuentas_patrimonio])
    patrimonio_saldo = patrimonio_haber - patrimonio_debe
    print(f"Patrimonio - Debe: {patrimonio_debe}, Haber: {patrimonio_haber}, Saldo: {patrimonio_saldo}")

    if patrimonio_saldo > 0:
        patrimonio_debe = Decimal('0.0')
        patrimonio_haber = patrimonio_saldo
    else:
        patrimonio_debe = abs(patrimonio_saldo)
        patrimonio_haber = Decimal('0.0')


    # Calcular balance_general_debe y balance_general_haber
    balance_general_debe = activos_debe + pasivos_debe + patrimonio_debe
    balance_general_haber = activos_haber + pasivos_haber + patrimonio_haber
    print(f"Balance General - Debe: {balance_general_debe}, Haber: {balance_general_haber}")

    # Crear la instancia de balance general
    balance_general = BalanceGeneral.objects.create(
        fecha=fecha_actual,
        activos_saldo=activos_saldo,
        activos_debe=activos_debe,
        activos_haber=activos_haber,
        pasivos_saldo=pasivos_saldo,
        pasivos_debe=pasivos_debe,
        pasivos_haber=pasivos_haber,
        patrimonio_saldo=patrimonio_saldo,
        patrimonio_debe=patrimonio_debe,
        patrimonio_haber=patrimonio_haber,
        balance_general_debe=balance_general_debe,
        balance_general_haber=balance_general_haber
    )
    print(f"Balance General creado: {balance_general}")

    # Guardar cada una de las cuentas filtradas en registros de CuentasBalanceGeneral
    cuentas_balance_general = []
    for cuenta in cuentas_activos:
        cuenta_balance = CuentasBalanceGeneral(
            codigo=cuenta.codigo_cuenta,
            nombre=cuenta.nombre,
            categoria=cuenta.categoria,
            saldo_deudor=cuenta.saldado_deudor,
            saldo_acreedor=cuenta.saldado_acreedor,
            id_balance_general=balance_general
        )
        cuenta_balance.save()
        cuentas_balance_general.append(cuenta_balance)
        print(f"Cuenta Activo guardada: {cuenta_balance}")

    for cuenta in cuentas_pasivos:
        cuenta_balance = CuentasBalanceGeneral(
            codigo=cuenta.codigo_cuenta,
            nombre=cuenta.nombre,
            categoria=cuenta.categoria,
            saldo_deudor=cuenta.saldado_deudor,
            saldo_acreedor=cuenta.saldado_acreedor,
            id_balance_general=balance_general
        )
        cuenta_balance.save()
        cuentas_balance_general.append(cuenta_balance)
        print(f"Cuenta Pasivo guardada: {cuenta_balance}")

    for cuenta in cuentas_patrimonio:
        cuenta_balance = CuentasBalanceGeneral(
            codigo=cuenta.codigo_cuenta,
            nombre=cuenta.nombre,
            categoria=cuenta.categoria,
            saldo_deudor=cuenta.saldado_deudor,
            saldo_acreedor=cuenta.saldado_acreedor,
            id_balance_general=balance_general
        )
        cuenta_balance.save()
        cuentas_balance_general.append(cuenta_balance)
        print(f"Cuenta Patrimonio guardada: {cuenta_balance}")

    return balance_general, cuentas_activos, cuentas_pasivos, cuentas_patrimonio

def balance_general(request):
    # Obtener todos los balances generales
    balances_generales = BalanceGeneral.objects.all().order_by('-id_balance_general')

    # Verificar si se selecciona un balance general específico
    balance_id = request.GET.get('balance_general')
    balance_seleccionado = None
    cuentas_activos, cuentas_pasivos, cuentas_patrimonio = [], [], []

    if balance_id:
        try:
            balance_seleccionado = BalanceGeneral.objects.get(id_balance_general=balance_id)
            cuentas_activos = CuentasBalanceGeneral.objects.filter(id_balance_general=balance_id, categoria='Activos')
            cuentas_pasivos = CuentasBalanceGeneral.objects.filter(id_balance_general=balance_id, categoria='Pasivos')
            cuentas_patrimonio = CuentasBalanceGeneral.objects.filter(id_balance_general=balance_id, categoria='Patrimonio')
        except BalanceGeneral.DoesNotExist:
            balance_seleccionado = None

    # Verificar si se solicita generar un nuevo balance general
    if request.GET.get('generar_balance_general') == 'true':
        balance_seleccionado, cuentas_activos, cuentas_pasivos, cuentas_patrimonio = generar_balance_general()
        
        return HttpResponseRedirect(reverse('balance_general') + f'?balance_general={balance_seleccionado.id_balance_general}')


    # Renderizar la plantilla con los datos obtenidos
    return render(request, 'balance_general.html', {
    'balances_generales': balances_generales,
    'balance_seleccionado': balance_seleccionado,
    'activos_saldo': balance_seleccionado.activos_saldo if balance_seleccionado else None,
    'cuentas_activos': cuentas_activos,
    'pasivos_saldo': balance_seleccionado.pasivos_saldo if balance_seleccionado else None,
    'cuentas_pasivos': cuentas_pasivos,
    'patrimonio_saldo': balance_seleccionado.patrimonio_saldo if balance_seleccionado else None,
    'cuentas_patrimonio': cuentas_patrimonio,
    # Balance
    'activos_debe': balance_seleccionado.activos_debe if balance_seleccionado else None,
    'activos_haber': balance_seleccionado.activos_haber if balance_seleccionado else None,
    'pasivos_debe': balance_seleccionado.pasivos_debe if balance_seleccionado else None,
    'pasivos_haber': balance_seleccionado.pasivos_haber if balance_seleccionado else None,
    'patrimonio_debe': balance_seleccionado.patrimonio_debe if balance_seleccionado else None,
    'patrimonio_haber': balance_seleccionado.patrimonio_haber if balance_seleccionado else None,
    'balance_general_debe': balance_seleccionado.balance_general_debe if balance_seleccionado else None,
    'balance_general_haber': balance_seleccionado.balance_general_haber if balance_seleccionado else None,
})
 
def libro_mayor(request):
    return render(request, 'libro_mayor.html')

def cierre_contable(request):
    return render(request, 'cierre_contable.html')





def handle_not_found(request, exception):
    return redirect('home')
