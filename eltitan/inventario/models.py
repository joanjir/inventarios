from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

# Create your models here.


class Categoria(models.Model):
    name = models.CharField(max_length=150, verbose_name='Nombre', unique=True)
    desc = models.CharField(max_length=500, null=True, blank=True, verbose_name='Descripción')

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"

    def __str__(self):
        return self.name

    



class Producto(models.Model):
    code = models.CharField(null=True, blank=True, verbose_name='Código', unique=True, max_length=150)
    name = models.CharField(max_length=150, verbose_name='Nombre', unique=True)
    cat = models.ForeignKey(Categoria, on_delete=models.CASCADE, verbose_name='Categoría')
    cant_dis= models.IntegerField(verbose_name='Cantidad disponible', default= 0)
    inversion =  models.DecimalField(verbose_name="Inversion", max_digits=50, decimal_places=2,default=0)
    precio_venta = models.DecimalField(verbose_name='Precio de venta', max_digits=50, decimal_places=2,default=0)
    ingresos = models.DecimalField(verbose_name='Ingreso', max_digits=50, decimal_places=2,default=0)
    ganancia = models.DecimalField(verbose_name='Ganancia', max_digits=50, decimal_places=2,default=0)
    
    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"

    def __str__(self):
        return self.name
    
    def actualizar_inversion_y_disponibilidad(self):
        compras = self.compra_set.all()
        total_inversion = sum(compra.cant * compra.precio for compra in compras)
        self.inversion = total_inversion
        self.cant_dis = sum(compra.cant for compra in compras)
        self.save(update_fields=['inversion', 'cant_dis'])
        
    
        
    def actualizar_ingresos_y_ganancias(self):
        self.ingresos = self.cant_dis * self.precio_venta
        self.ganancia = self.ingresos - self.inversion
        self.save(update_fields=['ingresos', 'ganancia'])
        
    
class Compra(models.Model):
    producto =  models.ForeignKey(Producto, verbose_name="Producto", on_delete=models.CASCADE)
    cant = models.IntegerField(verbose_name="Cantidad de productos comprados")
    precio = models.DecimalField(verbose_name="Precio de compra", max_digits=10, decimal_places=2)
    fecha = models.DateField(verbose_name="Fecha de compra", auto_now=False, auto_now_add=False)
    

    class Meta:
        verbose_name = "Compra"
        verbose_name_plural = "Compras"
        
        
class Venta(models.Model):
    producto = models.ForeignKey('Producto', verbose_name="Producto", on_delete=models.CASCADE)
    cantidad = models.IntegerField(verbose_name="Cantidad de productos vendidos")
    fecha = models.DateField(verbose_name="Fecha de venta", auto_now_add=True)

    class Meta:
        verbose_name = "Venta"
        verbose_name_plural = "Ventas"

    def str(self):
        return f"Venta de {self.cantidad} {self.producto} el {self.fecha}"
    
@receiver([post_save, post_delete], sender=Compra)
def actualizar_inversion_y_disponibilidad_producto(sender, instance, **kwargs):
    producto = instance.producto
    producto.actualizar_inversion_y_disponibilidad()
    producto.actualizar_ingresos_y_ganancias()

@receiver(post_save, sender=Producto)
def actualizar_ingresos_y_ganancias_por_precio(sender, instance, **kwargs):
    if instance.precio_venta is not None:
          if kwargs.get('update_fields') is None or 'precio_venta' in kwargs['update_fields']:
            instance.actualizar_ingresos_y_ganancias()
                           
@receiver(post_save, sender=Producto)
def generar_codigo(sender, instance, created, **kwargs):
    if created and not instance.code:
        categoria_id = str(instance.cat_id).zfill(2)
        print(categoria_id)
        producto_id = str(instance.id).zfill(2)
        instance.code = categoria_id + producto_id
        print(instance.code)
        instance.save()
 
 
@receiver(post_save, sender=Venta)
def actualizar_disponibilidad_venta(sender, instance, created, **kwargs):
    if created:
        producto = instance.producto
        cant_vendida = instance.cantidad
        if cant_vendida > producto.cant_dis:
            raise ValueError("Cantidad insuficiente disponible para la venta.")
        producto.cant_dis -= cant_vendida

        # Obtener el precio de compra del producto
        compra = Compra.objects.filter(producto=producto).order_by('-fecha').first()
        if compra:
            precio_compra = compra.precio
        else:
            precio_compra = 0

        producto.inversion = producto.cant_dis * precio_compra
        producto.ingresos = producto.cant_dis * producto.precio_venta  # Utilizar el precio de compra en el cálculo del ingreso
        producto.ganancia = producto.ingresos - producto.inversion
        producto.save(update_fields=['cant_dis', 'ingresos', 'ganancia', 'inversion'])
   





    
