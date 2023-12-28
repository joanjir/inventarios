import json
from django.core.exceptions import ValidationError
from django.db import models
from django.core.files.base import ContentFile
from django.core import serializers
from qrcode import make
from PIL import Image
import io
from django.db.models.signals import post_save, post_delete, pre_delete, pre_save
from django.dispatch import receiver
from django.forms import model_to_dict
from django.contrib import messages
from django.shortcuts import redirect

# Create your models here.

class Almacen(models.Model):
   nombre = models.CharField(max_length=200)
   ubicacion = models.CharField(max_length=200)
   responsable = models.CharField(max_length=200)
   activo = models.BooleanField(default=True)

   class Meta:
       verbose_name = 'Almacen'
       verbose_name_plural = 'Almacenes'
       
class UnidadMedida(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    prefijo = models.CharField(max_length=10, blank=True)
    activo = models.BooleanField(default=True)
    

    def __str__(self):
        return f'{self.prefijo} {self.nombre}'
    
    
    class Meta:
        verbose_name_plural = "Unidades de medida" 
class Categoria(models.Model):
    name = models.CharField(max_length=150, verbose_name='Nombre', unique=True)
    desc = models.CharField(max_length=500, null=True, blank=True, verbose_name='Descripción')
    activo = models.BooleanField(default=True, verbose_name='Estado')

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if self.activo == False and Producto.objects.filter(cat=self).exists():
            raise ValidationError("No se puede desactivar una categoría que está vinculada a productos.")
        super().save(*args, **kwargs)

class Producto(models.Model):
    code = models.CharField(null=True, blank=True, verbose_name='Código', unique=True, max_length=150)
    name = models.CharField(max_length=150, verbose_name='Nombre', unique=True)
    cat = models.ForeignKey(Categoria, on_delete=models.CASCADE, verbose_name='Categoría')
    cant_dis= models.IntegerField(verbose_name='Cantidad disponible', default= 0)
    unidad_medida = models.ForeignKey(UnidadMedida, on_delete=models.CASCADE)
    inversion =  models.DecimalField(verbose_name="Inversion", max_digits=50, decimal_places=2,default=0)
    precio_venta = models.DecimalField(verbose_name='Precio de venta', max_digits=50, decimal_places=2,default=0)
    ingresos = models.DecimalField(verbose_name='Ingreso', max_digits=50, decimal_places=2,default=0)
    ganancia = models.DecimalField(verbose_name='Ganancia', max_digits=50, decimal_places=2,default=0)
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
    
    
      
class Compra(models.Model):
    fechaCompra = models.DateField(verbose_name="Fecha de compra", auto_now=False, auto_now_add=False)
    total = models.DecimalField(default=0.00, max_digits=9, decimal_places=2)
    numFactura = models.CharField(max_length=100)
    fechaFactura = models.DateField()
    ESTADO_CHOICES = (
        ('ACT', 'Activa'),
        ('ANU', 'Anulada'),
    )
    estado = models.CharField(max_length=3, choices=ESTADO_CHOICES, default='ACT')


    def toJSON(self):
        item = model_to_dict(self)
        item['total'] = format(self.total, '.2f')

        return item

    
    class Meta:
        verbose_name = 'Compra'
        verbose_name_plural = 'Compras'
        ordering = ['id']
   
class DetalleCompra(models.Model):
    compra = models.ForeignKey(Compra, verbose_name="Compra", on_delete=models.CASCADE)
    producto =  models.ForeignKey(Producto, verbose_name="Producto", on_delete=models.CASCADE)
    cant = models.IntegerField(verbose_name="Cantidad de productos comprados")
    precio = models.DecimalField(verbose_name="Precio de compra", max_digits=10, decimal_places=2)
    costo = models.FloatField(default=0)

    
    def toJSON(self):
        item = model_to_dict(self, exclude=['compra'])
        item['producto'] = self.producto.toJSON()
        item['precio'] = format(self.precio, '.2f')
        item['producto']['name'] = self.producto.name  # Agregar el campo "name" del produ
        return item

    class Meta:
        verbose_name = "Compra de producto"
        verbose_name_plural = "Compras de productos"

     
class Venta(models.Model):
    producto = models.ForeignKey('Producto', verbose_name="Producto", on_delete=models.CASCADE)
    cantidad = models.IntegerField(verbose_name="Cantidad de productos vendidos")
    fecha = models.DateField(verbose_name="Fecha de venta", auto_now_add=True)

  
    class Meta:
        verbose_name = "Venta"
        verbose_name_plural = "Ventas"

    def str(self):
        return f"Venta de {self.cantidad} {self.producto} el {self.fecha}"
   
   
                        
@receiver(post_save, sender=Producto)
def generar_codigo(sender, instance, created, **kwargs):
    if created and not instance.code:
        categoria_id = str(instance.cat_id).zfill(2)
        producto_id = str(instance.id).zfill(2)
        instance.code = categoria_id + producto_id
        instance.save()
 

 



    
