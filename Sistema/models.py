from django.db import models
LIBRO_MAYOR_ACTUAL = 1

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
    salario = models.DecimalField(max_digits=12, decimal_places=2)
    puesto = models.CharField(max_length=50)
    horas_semanales = models.IntegerField(default=0)
    pago_diario = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    afp = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    septimo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    incaf = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    vacaciones = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    isss = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    aguinaldo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    costo_real_mensual = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.nombre} - {self.puesto}"

