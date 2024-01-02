from django.urls import path
from inventario.config.unidmed.views import listUnidadMedida, createUnidadMedida
from inventario.config.catalogo.views import listCatalogo, createCatalogo, deleteCatalogo, verificarCategoria, editarCatalogo
from inventario.config.producto.views import listProducto, createProducto, editProducto
from inventario.config.compras.views import compras, buscar_producto, guardar_compra, list_compra, editar_compra, editar, eliminar_compra
from inventario.config.empleado.views import empleado_create, empleado_list, eliminar_empleado
from inventario.config.almacenes.views import create_almacen, list_almacen
from inventario.config.puntvent.views import list_puntvemt, create_puntvemt


urlpatterns = [
    ## Administraciones
    #Empleados
    path('administraciones/listarEmpleados/', empleado_list, name='empleado_list'),
    path('administraciones/crearEmpleado/', empleado_create, name='empleado_create'),
    path('administraciones/eliminarEmpleado/<int:empleado_id>/', eliminar_empleado, name='eliminar_empleado'),
    
    #Almacenes
    path('administraciones/crearAlmacen/', create_almacen, name='create_almacen'),
    path('administraciones/listarAlmacenes/', list_almacen, name='list_almacen'),

    #Puntos de ventas
    path('administraciones/crearPuntoVenta/', create_puntvemt, name='create_puntvemt'),
    path('administraciones/listarPuntoVentas/', list_puntvemt, name='list_puntvemt'),

    
    #Unidad de medida 
    path('administraciones/listarUnidadMedida/', listUnidadMedida, name='listUnidadMedida'),
    path('administraciones/crearUnidadMedida/', createUnidadMedida, name='createUnidadMedida'),



    ## Inventarios
    
    #Categorias
    path('listarCategoria/', listCatalogo, name='listCatalogo'),
    path('crearCategoria/', createCatalogo, name='crearCatalogo'),
    path('eliminarCategoria/<int:pk>/', deleteCatalogo, name='deleteCatalogo'),
    path('editarCategoria/<int:pk>/', editarCatalogo, name='editarCatalogo'),
    path('verificarCategoria/<int:pk>/', verificarCategoria, name='verificarCategoria'),
    
    #Productos
    path('listarProducto/', listProducto, name='listProducto'),
    path('crearProducto/', createProducto, name='createProducto'),
    path('editarProducto/<int:pk>/', editProducto, name='editProducto'),


    ##Entradas y Salidas
    
    #Compras
    path('comprarProductos/', compras, name='compras'),
    path('buscar_producto/', buscar_producto, name='buscar_producto'),
    path('guardar_compra/', guardar_compra, name='guardar_compra'),
    path('listarCompra/', list_compra, name='list_compra'),
    path('editar_compra/<int:compra_id>/', editar_compra, name='editar_compra'),
    path('editar/', editar, name='editar'),
    path('eliminar_compra/<int:compra_id>/', eliminar_compra, name='eliminar_compra'),
]

