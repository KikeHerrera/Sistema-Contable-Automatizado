# Generated by Django 4.2.16 on 2024-11-03 17:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Sistema', '0004_cuentacontable_saldado_acreedor_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='BalanceGeneral',
            fields=[
                ('id_balance_general', models.AutoField(primary_key=True, serialize=False)),
                ('fecha', models.DateField()),
                ('activos', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('pasivos', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('patrimonio', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
            ],
        ),
        migrations.CreateModel(
            name='EstadoDeCapital',
            fields=[
                ('id_estado_capital', models.AutoField(primary_key=True, serialize=False)),
                ('fecha', models.DateField()),
                ('patrimonio_final', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
            ],
        ),
        migrations.CreateModel(
            name='EstadoDeResultado',
            fields=[
                ('id_estado_resultado', models.AutoField(primary_key=True, serialize=False)),
                ('fecha', models.DateField()),
                ('ingresos_operativos', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('costos_venta', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('utilidad_bruta', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
            ],
        ),
        migrations.AlterField(
            model_name='empleado',
            name='afp',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='empleado',
            name='aguinaldo',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='empleado',
            name='costo_real_mensual',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
        ),
        migrations.AlterField(
            model_name='empleado',
            name='horas_semanales',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='empleado',
            name='incaf',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='empleado',
            name='isss',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='empleado',
            name='pago_diario',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='empleado',
            name='septimo',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='empleado',
            name='vacaciones',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.CreateModel(
            name='CuentasEstadoDeResultado',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.CharField(max_length=20)),
                ('nombre', models.CharField(max_length=100)),
                ('categoria', models.CharField(max_length=50)),
                ('saldo_deudor', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('saldo_acreedor', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('id_estado_resultado', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cuentas', to='Sistema.estadoderesultado')),
            ],
        ),
        migrations.CreateModel(
            name='CuentasEstadoDeCapital',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.CharField(max_length=20)),
                ('nombre', models.CharField(max_length=100)),
                ('categoria', models.CharField(max_length=50)),
                ('saldo_deudor', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('saldo_acreedor', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('id_estado_capital', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cuentas', to='Sistema.estadodecapital')),
            ],
        ),
        migrations.CreateModel(
            name='CuentasBalanceGeneral',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.CharField(max_length=20)),
                ('nombre', models.CharField(max_length=100)),
                ('categoria', models.CharField(max_length=50)),
                ('saldo_deudor', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('saldo_acreedor', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('id_balance_general', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cuentas', to='Sistema.balancegeneral')),
            ],
        ),
    ]
