# Generated by Django 4.2.16 on 2024-11-05 18:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Sistema', '0013_rename_id_estado_resultado_cuentasauxiliaresestadodecapital_id_estado_capital'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cuentasauxiliaresestadodecapital',
            name='id_estado_capital',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cuentas_auxiliares', to='Sistema.cuentasestadodecapital'),
        ),
    ]
