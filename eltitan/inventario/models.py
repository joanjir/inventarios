import json
from django.core.exceptions import ValidationError
from django.db import models
from django.core.files.base import ContentFile
from django.core import serializers
import io
from django.db.models.signals import post_save, post_delete, pre_delete, pre_save
from django.dispatch import receiver
from django.forms import model_to_dict
from django.contrib import messages
from django.shortcuts import redirect

# Create your models here.


class Almacen(models.Model):
    nombre = models.CharField(max_length=200, verbose_name='Nombre')
    ubicacion = models.CharField(max_length=200, verbose_name='Ubicación')
    activo = models.BooleanField(default=True, verbose_name='Activo')
    central = models.BooleanField(default=False, verbose_name='Central')

    def __str__(self):
        return self.nombre


class PuntoVenta(models.Model):
    nombre = models.CharField(max_length=200, verbose_name='Nombre')
    ubicacion = models.CharField(max_length=200, verbose_name='Ubicación')
    activo = models.BooleanField(default=True, verbose_name='Activo')

    def __str__(self):
        return self.nombre


class Empleado(models.Model):
    TIPO_LUGAR_CHOICES = [
        ('Almacen', 'Almacén'),
        ('PuntoVenta', 'Punto de Venta')
    ]

    nombre = models.CharField(max_length=200, verbose_name='Nombre')
    apellido = models.CharField(max_length=200, verbose_name='Apellidos')
    dni = models.CharField(max_length=11, unique=True, verbose_name='DNI')
    telefono = models.CharField(max_length=15, verbose_name='Teléfono')
    direccion = models.TextField(verbose_name='Dirección')
    puesto = models.ForeignKey(
        'Puesto', on_delete=models.CASCADE, verbose_name='Puesto')
    fecha_contratacion = models.DateField(verbose_name='Fecha de contratación')
    tipo_lugar = models.CharField(
        max_length=10, choices=TIPO_LUGAR_CHOICES, null=True)
    punto_venta = models.OneToOneField(
        'PuntoVenta', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Punto de Venta')
    almacenes = models.ManyToManyField('Almacen', verbose_name='Almacenes')
    imagen = models.ImageField(
        upload_to='empleados/', verbose_name='Imagen', null=True, blank=True)

    def __str__(self):
        return self.nombre


class Puesto(models.Model):
    nombre = models.CharField(max_length=200)

    def __str__(self):
        return self.nombre


class UnidadMedida(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    prefijo = models.CharField(max_length=10, blank=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.prefijo} | {self.nombre}'

    class Meta:
        verbose_name_plural = "Unidades de medida"


class Categoria(models.Model):
    name = models.CharField(max_length=150, verbose_name='Nombre', unique=True)
    desc = models.CharField(max_length=500, null=True,
                            blank=True, verbose_name='Descripción')
    activo = models.BooleanField(default=True, verbose_name='Estado')

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.activo == False and Producto.objects.filter(cat=self).exists():
            raise ValidationError(
                "No se puede desactivar una categoría que está vinculada a productos.")
        super().save(*args, **kwargs)


class Producto(models.Model):
    code = models.CharField(null=True, blank=True,
                            verbose_name='Código', unique=True, max_length=150)
    name = models.CharField(max_length=150, verbose_name='Nombre', unique=True)
    cat = models.ForeignKey(
        Categoria, on_delete=models.CASCADE, verbose_name='Categoría')
    cant_dis = models.DecimalField(
        verbose_name='Cantidad disponible', default=0, max_digits=10, decimal_places=2)
    unidad_medida = models.ForeignKey(UnidadMedida, on_delete=models.CASCADE)
    precio_venta = models.DecimalField(
        verbose_name='Precio de venta minoritario', max_digits=50, decimal_places=2, default=0)
    precio_venta_m = models.DecimalField(
        verbose_name='Precio de venta mayoritario', max_digits=50, decimal_places=2, default=0)
    activo = models.BooleanField(default=True)

    def toJSON(self):
        item = model_to_dict(self)
        item['cat'] = model_to_dict(self.cat)
        return item

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"

    def __str__(self):
        return self.name


class OrigenDestino(models.Model):
    almacen = models.OneToOneField(
        Almacen, on_delete=models.CASCADE, null=True, blank=True)
    punto_venta = models.OneToOneField(
        PuntoVenta, on_delete=models.CASCADE, null=True, blank=True)
    tipo = models.CharField(max_length=200)

    def __str__(self):
        if self.almacen:
            return f"Almacen | {self.almacen.nombre}"
        else:
            return f"Punto de venta | {self.punto_venta.nombre}"


class Movimiento(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    origen = models.ForeignKey(
        OrigenDestino, related_name='+', on_delete=models.CASCADE)
    destino = models.ForeignKey(
        OrigenDestino, related_name='+', on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)

    def clean(self):
        # Verificar que el origen y el destino sean diferentes
        if self.origen == self.destino:
            raise ValidationError(
                "El origen y el destino no pueden ser el mismo.")

        # Verificar que haya suficiente cantidad del producto en el almacén o punto de venta de origen
        producto_origen = Producto.objects.get(id=self.producto.id)
        if self.origen.tipo == 'almacen':
            if producto_origen.cant_almacen < self.cantidad:
                raise ValidationError(
                    "No hay suficiente cantidad del producto en el almacén de origen.")
        elif self.origen.tipo == 'punto_venta':
            if producto_origen.cant_punto_venta < self.cantidad:
                raise ValidationError(
                    "No hay suficiente cantidad del producto en el punto de venta de origen.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.producto.name} - {self.cantidad} - {self.origen} -> {self.destino}'


class Compra(models.Model):
    fechaCompra = models.DateField(
        verbose_name="Fecha de compra", auto_now=False, auto_now_add=False)
    total = models.DecimalField(default=0.00, max_digits=9, decimal_places=2)
    numFactura = models.CharField(max_length=100)
    fechaFactura = models.DateField()
    ESTADO_CHOICES = (
        ('ACT', 'Activa'),
        ('ANU', 'Anulada'),
    )
    estado = models.CharField(
        max_length=3, choices=ESTADO_CHOICES, default='ACT')

    def toJSON(self):
        item = model_to_dict(self)
        item['total'] = format(self.total, '.2f')

        return item

    class Meta:
        verbose_name = 'Compra'
        verbose_name_plural = 'Compras'
        ordering = ['id']


class DetalleCompra(models.Model):
    compra = models.ForeignKey(
        Compra, verbose_name="Compra", on_delete=models.CASCADE)
    producto = models.ForeignKey(
        Producto, verbose_name="Producto", on_delete=models.CASCADE)
    cant = models.DecimalField(
        verbose_name="Cantidad de productos comprados", max_digits=10, decimal_places=2)
    precio = models.DecimalField(
        verbose_name="Precio de compra", max_digits=10, decimal_places=2)
    costo = models.FloatField(default=0)

    def toJSON(self):
        item = model_to_dict(self, exclude=['compra'])
        item['producto'] = self.producto.toJSON()
        item['precio'] = format(self.precio, '.2f')
        # Agregar el campo "name" del produ
        item['producto']['name'] = self.producto.name
        return item

    class Meta:
        verbose_name = "Compra de producto"
        verbose_name_plural = "Compras de productos"


class Venta(models.Model):
    producto = models.ForeignKey(
        'Producto', verbose_name="Producto", on_delete=models.CASCADE)
    cantidad = models.IntegerField(
        verbose_name="Cantidad de productos vendidos")
    fecha = models.DateField(verbose_name="Fecha de venta", auto_now_add=True)

    class Meta:
        verbose_name = "Venta"
        verbose_name_plural = "Ventas"

    def str(self):
        return f"Venta de {self.cantidad} {self.producto} el {self.fecha}"


class Inventario(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    almacen = models.ForeignKey(
        Almacen, null=True, blank=True, on_delete=models.SET_NULL)
    punto_venta = models.ForeignKey(
        PuntoVenta, null=True, blank=True, on_delete=models.SET_NULL)
    cantidad = models.DecimalField(
        verbose_name='Cantidad en inventario', default=0, max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.producto.name} - {self.cantidad}'


@receiver(post_save, sender=Producto)
def generar_codigo(sender, instance, created, **kwargs):
    if created and not instance.code:
        categoria_id = str(instance.cat_id).zfill(2)
        producto_id = str(instance.id).zfill(2)
        instance.code = categoria_id + producto_id
        instance.save()


@receiver(post_save, sender=Almacen)
def create_origen_destino_after_almacen_saved(sender, instance, created, **kwargs):
    if created:
        OrigenDestino.objects.create(almacen=instance)


@receiver(post_save, sender=PuntoVenta)
def create_origen_destino_after_punto_venta_saved(sender, instance, created, **kwargs):
    if created:
        OrigenDestino.objects.create(punto_venta=instance)
