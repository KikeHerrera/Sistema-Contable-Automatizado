# Generated by Django 4.2.16 on 2024-11-03 00:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Sistema', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaccion',
            name='contenido',
            field=models.TextField(default='nothing'),
            preserve_default=False,
        ),
    ]
