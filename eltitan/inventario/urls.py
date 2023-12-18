from django.urls import path
from inventario.config.catalogo.views import listCatalogo, createCatalogo, deleteCatalogo, verificarCategoria, editarCatalogo



urlpatterns = [
    path('listarCategoria/', listCatalogo, name='listCatalogo'),
    path('crearCategoria/', createCatalogo, name='crearCatalogo'),
    path('eliminarCategoria/<int:pk>/', deleteCatalogo, name='deleteCatalogo'),
    path('editarCategoria/<int:pk>/', editarCatalogo, name='editarCatalogo'),
    path('verificarCategoria/<int:pk>/', verificarCategoria, name='verificarCategoria'),

    
]

