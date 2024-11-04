from django.contrib import admin

# Register your models here.
from .models import CuentaContable, BalanceGeneral, CuentasBalanceGeneral, EstadoDeResultado, EstadoDeCapital

# Registrar cada uno de los modelos para que aparezcan en el panel de administración
admin.site.register(CuentaContable)
admin.site.register(BalanceGeneral)
admin.site.register(CuentasBalanceGeneral)
admin.site.register(EstadoDeResultado)
admin.site.register(EstadoDeCapital)