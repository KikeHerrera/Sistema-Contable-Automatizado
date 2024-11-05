from django.http import HttpResponseRedirect
from django.urls import reverse
from decimal import Decimal
from django.db.models import Sum
from datetime import date, timedelta, timezone
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm , AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from .forms import TransaccionForm, CuentaContable, AsientoCustomForm
from .models import Asiento, Transaccion, PartidaDiaria, CuentaContable, BalanceGeneral, CuentasBalanceGeneral, EstadoDeResultado, CuentasEstadoDeResultado, CuentasAuxiliaresEstadoDeResultado
from .utils import filtrar_o_crear_partida_diaria
from .models import Empleado
from .forms import EmpleadoForm 
from django.db import transaction


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
        'partida_seleccionada': partida_seleccionada
    })

def home(request):
    return render(request, 'home.html', {"username":request.user.username})

def cerrarSesion(request):
    logout(request)
    return redirect("home")


def registrar_transaccion(fecha_operacion, contenido, cuenta_deudor, cuenta_acreedor, monto):
    # Crear el objeto Transaccion y asignar valores
    transaccion = Transaccion(
        fecha_operacion=fecha_operacion,
        contenido=contenido,
        total_debe=monto,
        total_haber=monto,
        id_partida_diaria=filtrar_o_crear_partida_diaria()
    )
    transaccion.save()
    
    # Actualizar saldos de las cuentas
    cuenta_deudor.saldo_debe += monto
    cuenta_deudor.save()
    
    cuenta_acreedor.saldo_haber += monto
    cuenta_acreedor.save()
    
    # Crear asientos contables
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
    
    return transaccion


def transaccion(request):
    if request.method == 'POST':
        formularioBase = TransaccionForm(request.POST)
        formularioAsientoContable = AsientoCustomForm(request.POST)

        if formularioBase.is_valid() and formularioAsientoContable.is_valid():
            # Extraer datos del formulario
            cuenta_deudor = formularioAsientoContable.cleaned_data['cuenta_deudor']
            cuenta_acreedor = formularioAsientoContable.cleaned_data['cuenta_acreedor']
            monto = formularioAsientoContable.cleaned_data['monto']
            fecha_operacion = formularioBase.cleaned_data['fecha_operacion']
            contenido = formularioBase.cleaned_data['contenido']

            # Llamar a la función registrar_transaccion para registrar la transacción y los asientos
            registrar_transaccion(fecha_operacion, contenido, cuenta_deudor, cuenta_acreedor, monto)

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

def saldar_acreedora(cuenta):
    # Calcular el saldo de la cuenta (Haber - Debe)
    saldo = cuenta.saldo_haber - cuenta.saldo_debe
    cuenta.saldo = saldo

    # Asignar el saldo correspondiente
    if saldo > 0:
        cuenta.saldado_acreedor = saldo
        cuenta.saldado_deudor = Decimal('0.0')
    else:
        cuenta.saldado_acreedor = Decimal('0.0')
        cuenta.saldado_deudor = abs(saldo)

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

    # Obtener todas las cuentas contables
    cuentas = CuentaContable.objects.all()

    # Inicializar saldos totales como Decimal
    total_debe = Decimal('0.0')
    total_haber = Decimal('0.0')

    # Sumar al total de debe y haber con las cuentas actualizadas
    for cuenta in cuentas:
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



def handle_not_found(request, exception):
    return redirect('home')


def estados_financieros(request):
    return render(request, 'estados_financieros.html')

def estado_de_capital(request):
    return render(request, 'estado_de_capital.html')



def saldar_a_cero(cuentas):
    for cuenta in cuentas:
        cuenta.saldado_deudor = 0
        cuenta.saldado_acreedor = 0        
        cuenta.saldo_debe = 0
        cuenta.saldo_haber = 0
        cuenta.save()
        print(f"Cuenta {cuenta.nombre} saldada a cero.")




def saldar_cuentas():
    # Obtener todas las cuentas contables
    cuentas = CuentaContable.objects.all()

    # Iterar sobre cada cuenta y saldarla
    for cuenta in cuentas:
        saldar(cuenta)

    print("Todas las cuentas han sido saldadas.")

def generar_balance_general(origen="Usuario"):
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
        detalle = origen,
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
 
def estado_de_resultados(request):
    # Obtener todos los estados de resultados ordenados por fecha
    estados_de_resultados = EstadoDeResultado.objects.all().order_by('-id_estado_resultado')

    # Inicialización de variables para evitar errores en el contexto
    informe_seleccionado = None
    cuentas_ingresos, cuentas_costos_venta, cuentas_gastos = [], [], []
    ingresos_totales, costos_venta_totales, gastos_totales = None, None, None
    utilidad_bruta, utilidad_neta = None, None

    # Verificar si se selecciona un estado específico
    informe_id = request.GET.get('estado_resultado')
    if informe_id:
        try:
            informe_seleccionado = EstadoDeResultado.objects.get(id_estado_resultado=informe_id)
            cuentas_ingresos = CuentasEstadoDeResultado.objects.filter(id_estado_resultado=informe_id, codigo__startswith="4.")
            cuentas_costos_venta = CuentasEstadoDeResultado.objects.filter(id_estado_resultado=informe_id, codigo__startswith="6.")
            cuentas_gastos = CuentasEstadoDeResultado.objects.filter(id_estado_resultado=informe_id, codigo__startswith="5.")
            
            # Obtener Cuentas Auxiliares
            ingresos_totales = CuentasAuxiliaresEstadoDeResultado.objects.filter(id_estado_resultado=informe_id, nombre="Ingresos Totales").first()
            costos_venta_totales = CuentasAuxiliaresEstadoDeResultado.objects.filter(id_estado_resultado=informe_id, nombre="Costos de Venta Totales").first()
            gastos_totales = CuentasAuxiliaresEstadoDeResultado.objects.filter(id_estado_resultado=informe_id, nombre="Gastos Totales").first()
            utilidad_bruta = CuentasAuxiliaresEstadoDeResultado.objects.filter(id_estado_resultado=informe_id, nombre="Utilidad Bruta").first()
            utilidad_neta = CuentasAuxiliaresEstadoDeResultado.objects.filter(id_estado_resultado=informe_id, nombre="Utilidad Neta").first()

        except EstadoDeResultado.DoesNotExist:
            informe_seleccionado = None

    return render(request, 'estado_de_resultados.html', {
        'estados_de_resultados_seleccionado': informe_seleccionado,
        'estados_de_resultados': estados_de_resultados,
        'ingresos_totales': ingresos_totales,
        'cuentas_ingresos': cuentas_ingresos,
        'costos_venta_totales': costos_venta_totales,
        'cuentas_costos_venta': cuentas_costos_venta,
        'cuentas_gastos': cuentas_gastos,
        'gastos_totales': gastos_totales,
        'utilidad_bruta': utilidad_bruta,
        'utilidad_neta': utilidad_neta,
    })


def calcular_proxima_fecha_cierre():
    """
    Calcula la próxima fecha de cierre contable, que será el 1 de junio o el 1 de enero.
    """
    fecha_hoy = date.today()

    # Calcular las próximas fechas de cierre (1 de enero y 1 de junio)
    proximo_cierre_junio = date(fecha_hoy.year, 6, 1)
    proximo_cierre_enero = date(fecha_hoy.year + 1, 1, 1)

    # Determinar cuál es la próxima fecha de cierre desde hoy
    if fecha_hoy <= proximo_cierre_junio:
        return proximo_cierre_junio
    else:
        return proximo_cierre_enero

def cierre_contable(request):
    # Define el estado del cierre contable
    cierre_activado = request.session.get('cierre_activado', False)
    fecha_cierre = calcular_proxima_fecha_cierre()

    # Calcular los días restantes para el próximo cierre
    dias_para_cierre = (fecha_cierre - date.today()).days if not cierre_activado else 0

    if request.method == 'POST':
        if not cierre_activado:
            # Confirmar el cierre contable
            request.session['cierre_activado'] = True
            cierre_activado = True
        else:
            # Ejecutar el cierre contable y generar los estados financieros
            print("sexo")
            generar_balance_general("Antes del Cierre Contable")
            generar_estado_capital()
            generar_estado_resultados()
            request.session['cierre_activado'] = False
        
        # Redirigir a la misma página de cierre contable después de confirmar o ejecutar el cierre
        return HttpResponseRedirect(reverse('cierre_contable'))

    return render(request, 'cierre_contable.html', {
        'cierre_activado': cierre_activado,
        'dias_para_cierre': dias_para_cierre,
    })

def generar_estado_capital():
    # Lógica para generar el estado de capital
    pass


def generar_estado_resultados():
    """
    Genera un nuevo Estado de Resultados y guarda los datos en la base de datos.
    Retorna la instancia del Estado de Resultados generado.
    """
    with transaction.atomic():
        # Crear una nueva instancia de Estado de Resultados
        estado_resultados = EstadoDeResultado.objects.create(fecha=date.today())

        # Filtrar las cuentas contables por categorías
        cuentas_ingresos = CuentaContable.objects.filter(codigo_cuenta__startswith="4.")
        cuentas_costos_venta = CuentaContable.objects.filter(codigo_cuenta__startswith="6.")
        cuentas_gastos = CuentaContable.objects.filter(codigo_cuenta__startswith="5.")

        # Crear y guardar cuentas relacionadas para ingresos, costos de venta y gastos
        for cuenta in cuentas_ingresos:
            CuentasEstadoDeResultado.objects.create(
                codigo=cuenta.codigo_cuenta,
                nombre=cuenta.nombre,
                categoria="Ingresos",
                saldo_deudor=cuenta.saldado_deudor,
                saldo_acreedor=cuenta.saldado_acreedor,
                id_estado_resultado=estado_resultados
            )

        for cuenta in cuentas_costos_venta:
            CuentasEstadoDeResultado.objects.create(
                codigo=cuenta.codigo_cuenta,
                nombre=cuenta.nombre,
                categoria="Costos de Venta",
                saldo_deudor=cuenta.saldado_deudor,
                saldo_acreedor=cuenta.saldado_acreedor,
                id_estado_resultado=estado_resultados
            )

        for cuenta in cuentas_gastos:
            CuentasEstadoDeResultado.objects.create(
                codigo=cuenta.codigo_cuenta,
                nombre=cuenta.nombre,
                categoria="Gastos",
                saldo_deudor=cuenta.saldado_deudor,
                saldo_acreedor=cuenta.saldado_acreedor,
                id_estado_resultado=estado_resultados
            )

        # Calcular Ingresos Totales
        ingresos_totales = CuentasAuxiliaresEstadoDeResultado(
            nombre="Ingresos Totales",
            saldo_debe=sum(cuenta.saldado_deudor for cuenta in cuentas_ingresos),
            saldo_haber=sum(cuenta.saldado_acreedor for cuenta in cuentas_ingresos),
            id_estado_resultado=estado_resultados
        )
        saldar_acreedora(ingresos_totales)
        ingresos_totales.save()

        # Calcular Costos de Venta Totales
        costos_venta_totales = CuentasAuxiliaresEstadoDeResultado(
            nombre="Costos de Venta Totales",
            saldo_debe=sum(cuenta.saldado_deudor for cuenta in cuentas_costos_venta),
            saldo_haber=sum(cuenta.saldado_acreedor for cuenta in cuentas_costos_venta),
            id_estado_resultado=estado_resultados
        )
        saldar(costos_venta_totales)
        costos_venta_totales.save()

        # Calcular Gastos Totales
        gastos_totales = CuentasAuxiliaresEstadoDeResultado(
            nombre="Gastos Totales",
            saldo_debe=sum(cuenta.saldado_deudor for cuenta in cuentas_gastos),
            saldo_haber=sum(cuenta.saldado_acreedor for cuenta in cuentas_gastos),
            id_estado_resultado=estado_resultados
        )
        saldar(gastos_totales)
        gastos_totales.save()

        # Calcular Utilidad Bruta (Ingresos Totales - Costos de Venta Totales)
        utilidad_bruta = CuentasAuxiliaresEstadoDeResultado(
            nombre="Utilidad Bruta",
            saldo_debe=ingresos_totales.saldado_deudor + costos_venta_totales.saldado_deudor,
            saldo_haber=ingresos_totales.saldado_acreedor + costos_venta_totales.saldado_acreedor,
            id_estado_resultado=estado_resultados
        )
        saldar_acreedora(utilidad_bruta)
        utilidad_bruta.save()

        # Calcular Utilidad Neta (Utilidad Bruta - Gastos Totales)
        utilidad_neta = CuentasAuxiliaresEstadoDeResultado(
            nombre="Utilidad Neta",
            saldo_debe=utilidad_bruta.saldado_deudor + gastos_totales.saldado_deudor,
            saldo_haber=utilidad_bruta.saldado_acreedor + gastos_totales.saldado_acreedor,
            id_estado_resultado=estado_resultados
        )
        saldar_acreedora(utilidad_neta)
        utilidad_neta.save()
      
        # Retornar la instancia del estado de resultados creado
        return estado_resultados
