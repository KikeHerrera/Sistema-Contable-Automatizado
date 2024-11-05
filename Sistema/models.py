from django.db import models
LIBRO_MAYOR_ACTUAL = 1
from decimal import Decimal

class LibroMayor(models.Model):
    # Tabla para representar el Libro Mayor
    id_libro_mayor = models.AutoField(primary_key=True)

    def __str__(self):
        return f"Libro Mayor {self.id_libro_mayor}"


class PartidaDiaria(models.Model):
    # Tabla para representar la partida diaria
    id_partida_diaria = models.AutoField(primary_key=True)
    fecha = models.DateField()
    id_libro_mayor = models.ForeignKey(LibroMayor, on_delete=models.CASCADE, related_name="partidas_diarias")

    def __str__(self):
        return f"Partida Diaria {self.id_partida_diaria} - Fecha: {self.fecha}"


class Transaccion(models.Model):
    # Tabla para representar las transacciones
    id_transaccion = models.AutoField(primary_key=True)
    fecha_operacion = models.DateField()
    contenido = models.TextField()
    fecha_registro = models.DateField(auto_now_add=True)  # Se guarda la fecha de registro automática
    total_debe = models.DecimalField(max_digits=12, decimal_places=2)
    total_haber = models.DecimalField(max_digits=12, decimal_places=2)
    id_partida_diaria = models.ForeignKey(PartidaDiaria, on_delete=models.CASCADE, related_name="transacciones")

    def __str__(self):
        return f"Transacción {self.id_transaccion} - Fecha Operación: {self.fecha_operacion}"


class CuentaContable(models.Model):
    # Tabla para representar las cuentas contables
    codigo_cuenta = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100)
    categoria = models.CharField(max_length=50)
    subcategoria = models.CharField(max_length=50, blank=True, null=True)
    saldo_debe = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    saldo_haber = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    saldo = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    saldado_acreedor = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    saldado_deudor = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f" {self.nombre} - {self.categoria} - {self.codigo_cuenta} "


class Asiento(models.Model):
    # Tabla para representar los asientos
    monto_debe = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    monto_haber = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    id_cuenta = models.ForeignKey('CuentaContable', on_delete=models.SET_NULL, null=True, blank=True, related_name="asientos")
    id_transaccion = models.ForeignKey(Transaccion, on_delete=models.CASCADE, related_name="asientos")

    def __str__(self):
        return f"Asiento {self.id} - Cuenta: {self.id_cuenta}- Debe: {self.monto_debe} / Haber: {self.monto_haber}"


class Empleado(models.Model):
    id_empleado = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    puesto = models.CharField(max_length=50)
    salario_nominal_diario = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    dias_semanales = models.IntegerField(default=0)
    septimo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    vacaciones = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    aguinaldo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    isss = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    afp = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    incaf = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    costo_real_semanal = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    FACTOR_AGUINALDO = Decimal(25)
    FACTOR_VACACIONES = Decimal(1.3)
    DIAS_VACACIONES = Decimal(15)

    def calcular_costos(self):
        # Cálculos usando Decimal para evitar errores de tipo
        self.septimo = self.salario_nominal_diario * Decimal(7)
        self.vacaciones = (self.salario_nominal_diario * self.DIAS_VACACIONES * self.FACTOR_VACACIONES) / Decimal(52)
        self.aguinaldo = (self.salario_nominal_diario * self.FACTOR_AGUINALDO) / Decimal(52)
        self.isss = (self.septimo + self.vacaciones) * Decimal(0.075)
        self.afp = (self.septimo + self.vacaciones) * Decimal(0.0775)
        self.incaf = (self.septimo + self.vacaciones) * Decimal(0.01)
        self.costo_real_semanal = (
            self.septimo + self.vacaciones + self.aguinaldo + self.isss + self.afp + self.incaf
        )

    def save(self, *args, **kwargs):
        # Calcular los costos antes de guardar
        self.calcular_costos()
        super().save(*args, **kwargs)

# Modelo para Balance General
class BalanceGeneral(models.Model):
    id_balance_general = models.AutoField(primary_key=True)
    fecha = models.DateField()
    detalle = models.CharField(max_length=50)

    activos_saldo = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    activos_debe = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    activos_haber = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    pasivos_saldo = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    pasivos_debe = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    pasivos_haber = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    patrimonio_saldo = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    patrimonio_debe = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    patrimonio_haber = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    balance_general_debe = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    balance_general_haber = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    def __str__(self):
        return f"Balance General {self.id_balance_general} {self.detalle} - Fecha: {self.fecha} "

# Modelo para Cuentas del Balance General
class CuentasBalanceGeneral(models.Model):
    codigo = models.CharField(max_length=20)
    nombre = models.CharField(max_length=100)
    categoria = models.CharField(max_length=50)
    saldo_deudor = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    saldo_acreedor = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    id_balance_general = models.ForeignKey(BalanceGeneral, on_delete=models.CASCADE, related_name="cuentas")

    def __str__(self):
        return f"Cuenta {self.codigo} - {self.nombre}"

# Modelo para Estado de Resultados
class EstadoDeResultado(models.Model):
    id_estado_resultado = models.AutoField(primary_key=True)
    fecha = models.DateField()

    def __str__(self):
        return f"Estado de Resultados {self.id_estado_resultado} - Fecha: {self.fecha}"
    

class CuentasEstadoDeResultado(models.Model):
    codigo = models.CharField(max_length=20)
    nombre = models.CharField(max_length=100)
    categoria = models.CharField(max_length=50)
    saldo_deudor = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    saldo_acreedor = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    id_estado_resultado = models.ForeignKey(EstadoDeResultado, on_delete=models.CASCADE, related_name="cuentas")

# Modelo para Cuentas del Estado de Resultados
class CuentasAuxiliaresEstadoDeResultado(models.Model):
    nombre = models.CharField(max_length=100)
    saldo_debe = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    saldo_haber = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    saldo = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    saldado_acreedor = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    saldado_deudor = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    id_estado_resultado = models.ForeignKey(EstadoDeResultado, on_delete=models.CASCADE, related_name="cuentas_auxiliares")


    def __str__(self):
        return f"Cuenta - {self.nombre}"
    
    
# Modelo para Estado de Capital
class EstadoDeCapital(models.Model):
    id_estado_capital = models.AutoField(primary_key=True)
    fecha = models.DateField()

    def __str__(self):
        return f"Estado de Capital {self.id_estado_capital} - Fecha: {self.fecha}"

# Modelo para Cuentas del Estado de Capital
class CuentasEstadoDeCapital(models.Model):
    codigo = models.CharField(max_length=20)
    nombre = models.CharField(max_length=100)
    categoria = models.CharField(max_length=50)
    saldo_deudor = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    saldo_acreedor = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    id_estado_capital = models.ForeignKey(EstadoDeCapital, on_delete=models.CASCADE, related_name="cuentas")

    def __str__(self):
        return f"Cuenta {self.codigo} - {self.nombre}"


class CuentasAuxiliaresEstadoDeCapital(models.Model):
    nombre = models.CharField(max_length=100)
    saldo_debe = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    saldo_haber = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    saldo = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    saldado_acreedor = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    saldado_deudor = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    id_estado_capital = models.ForeignKey(EstadoDeCapital, on_delete=models.CASCADE, related_name="cuentas_auxiliares")


    def __str__(self):
        return f"Cuenta - {self.nombre}"