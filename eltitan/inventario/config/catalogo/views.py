from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import HttpResponseRedirect, HttpResponse, Http404, JsonResponse, HttpResponseForbidden
from django.urls import reverse
from django.core.exceptions import ValidationError


from inventario.models import Categoria, Producto
from inventario.config.catalogo.forms import CategoryForm

# Create your views here.


def listCatalogo(request):
    cate= Categoria.objects.all()
    title = 'Categoría de los productos'
    return render(request,'config/listCatalogo.html', {'categs' : cate, 'title': title})


def createCatalogo(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():

            categoria = form.save(commit=False)
            
            categoria.save()

            message = "Categoría guardada correctamente."
            messages.success(request, message, extra_tags="create")

            return HttpResponseRedirect(reverse('listCatalogo'))
    else:
        form = CategoryForm()
        context = {
           'form': form,
           'title': 'Creación de una Categoría',
           'entity': 'Categoría de los productos',
           'action': 'add'
       }
    return render(request, 'config/createCatalogo.html', context)





def editarCatalogo(request, pk):
    category = get_object_or_404(Categoria, pk=pk)

    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            try:
                form.save()
                message = "Categoría editada correctamente."
                messages.success(request, message, extra_tags="edit")
            except ValidationError as e:
                messages.error(request, e.messages[0], extra_tags="error")
            return HttpResponseRedirect(reverse('listCatalogo'))
    else:
        form = CategoryForm(instance=category)
        context = {
            'form': form,

            'title': 'Edición de la Categoría',
            'entity': 'Categoría de los productos',
            'action': 'edit',
        }
    return render(request, 'config/editCatalogo.html', context)


def verificarCategoria(request, pk):
   service = get_object_or_404(Categoria, pk=pk)
   if Producto.objects.filter(cat=service).exists():
       return JsonResponse({'mensaje': 'La categoria tiene productos asociados y no puede ser eliminada.'}) 
   return JsonResponse({'mensaje': 'La categoria puede ser eliminada.'})

@csrf_exempt
@require_POST
def deleteCatalogo(request, pk):
    service = get_object_or_404(Categoria, pk=pk)
    service.delete()

    return JsonResponse({'mensaje': 'El registro ha sido eliminado exitosamente.'})



