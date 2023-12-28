from django.urls import path
from inventario.config.unidmed.views import listUnidadMedida, createUnidadMedida
from inventario.config.catalogo.views import listCatalogo, createCatalogo, deleteCatalogo, verificarCategoria, editarCatalogo
from inventario.config.producto.views import listProducto, createProducto, editProducto
from inventario.config.compras.views import compras, buscar_producto, guardar_compra, list_compra, editar_compra, editar, eliminar_compra


urlpatterns = [
    #Unidades de media
    path('listarUnidadMedida/', listUnidadMedida, name='listUnidadMedida'),
    path('crearUnidadMedida/', createUnidadMedida, name='createUnidadMedida'),

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



    path('comprarProductos/', compras, name='compras'),
    path('buscar_producto/', buscar_producto, name='buscar_producto'),
    path('guardar_compra/', guardar_compra, name='guardar_compra'),
    path('listarCompra/', list_compra, name='list_compra'),
    path('editar_compra/<int:compra_id>/', editar_compra, name='editar_compra'),
    path('editar/', editar, name='editar'),
    path('eliminar_compra/<int:compra_id>/', eliminar_compra, name='eliminar_compra'),
]

