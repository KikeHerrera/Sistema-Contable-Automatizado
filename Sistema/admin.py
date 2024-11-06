from django.contrib import admin

# Register your models here.
from .models import CuentaContable, BalanceGeneral, CuentasBalanceGeneral, EstadoDeResultado, EstadoDeCapital
from .models import Asiento, Transaccion, PartidaDiaria, CuentaContable, BalanceGeneral, CuentasBalanceGeneral, Empleado

# Registrar cada uno de los modelos para que aparezcan en el panel de administración
admin.site.register(BalanceGeneral)
admin.site.register(CuentasBalanceGeneral)
admin.site.register(EstadoDeResultado)
admin.site.register(EstadoDeCapital)
admin.site.register(PartidaDiaria)
admin.site.register(Empleado)
