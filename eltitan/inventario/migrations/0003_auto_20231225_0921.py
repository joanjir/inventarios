# Generated by Django 2.2.6 on 2023-12-25 14:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventario', '0002_remove_compra_subtotal'),
    ]

    operations = [
        migrations.RenameField(
            model_name='compra',
            old_name='fecha_compra',
            new_name='fechaCompra',
        ),
    ]