# Generated by Django 4.2.16 on 2024-11-05 18:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Sistema', '0015_alter_cuentasauxiliaresestadodecapital_id_estado_capital'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='estadodecapital',
            name='patrimonio_final_debe',
        ),
        migrations.RemoveField(
            model_name='estadodecapital',
            name='patrimonio_final_haber',
        ),
        migrations.RemoveField(
            model_name='estadodecapital',
            name='patrimonio_final_saldo',
        ),
    ]