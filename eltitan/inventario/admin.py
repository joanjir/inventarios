from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.forms import ModelForm
from .models import Almacen, PuntoVenta, Empleado, Puesto, UnidadMedida, Categoria, Producto, \
    Movimiento, Compra, DetalleCompra, Venta, Inventario, OrigenDestino

admin.site.register(Almacen)
admin.site.register(PuntoVenta)
admin.site.register(Empleado)
admin.site.register(Puesto)
admin.site.register(UnidadMedida)
admin.site.register(Categoria)

admin.site.register(Compra)
admin.site.register(DetalleCompra)
admin.site.register(Venta)
admin.site.register(OrigenDestino)



class MovimientoAdmin(admin.ModelAdmin):
   list_display = ('producto', 'cantidad', 'origen', 'destino', 'fecha')
   search_fields = ('producto__name', 'origen__tipo', 'destino__tipo')

admin.site.register(Movimiento, MovimientoAdmin)

@admin.register(Inventario)
class InventarioAdmin(admin.ModelAdmin):
    list_display = ('producto', 'almacen', 'punto_venta', 'cantidad')
    search_fields = ('producto__name', 'almacen__nombre',
                     'punto_venta__nombre')


class ProductoAdminForm(ModelForm):
    class Meta:
        model = Producto
        exclude = ['code', 'inversion', 'ingresos', 'ganancia', 'cant_dis']
        readonly_fields = ('delete',)


class ProductoAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'cat', 'precio_venta', 'cant_dis',
                    'editar_eliminar')  # Campos a mostrar en el listado
    list_filter = ('cat',)  # Filtros disponibles en el panel lateral
    search_fields = ('name', 'code')  # Campos de búsqueda
    form = ProductoAdminForm

    def editar_eliminar(self, obj):
        editar_url = reverse('admin:inventario_producto_change', args=[obj.id])
        eliminar_url = reverse(
            'admin:inventario_producto_delete', args=[obj.id])
        editar_button = format_html(
            '<input type="button" value="Editar" onclick="window.location.href=\'{}\';">', editar_url)
        eliminar_button = format_html(
            '<input type="button" value="Eliminar" onclick="window.location.href=\'{}\';" style="background-color: red; color: white;">', eliminar_url)
        return format_html('{} | {}', editar_button, eliminar_button)
    editar_eliminar.short_description = 'Acciones'


admin.site.register(Producto, ProductoAdmin)
