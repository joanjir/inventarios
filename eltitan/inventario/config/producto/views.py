from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect, HttpResponse, Http404, JsonResponse, HttpResponseForbidden
from django.urls import reverse
from django.core.exceptions import ValidationError



from inventario.models import Categoria, Producto, Compra
from inventario.config.producto.forms import ProductForm

# Create your views here.


def listProducto(request):
    prod= Producto.objects.all()
    title = 'Listado de productos'
    return render(request,'config/listProducto.html', {'prods' : prod, 'title': title})


def createProducto(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            message = "Producto guardada correctamente."
            messages.success(request, message, extra_tags="create")
            return redirect('listProducto') # Reemplaza 'product_list' con la URL de tu página de éxito
    else:
        form = ProductForm()
        context = {
           'form': form,
           'title': 'Registrar un producto',
           'entity': 'Listado de productos',
           'action': 'add'
       }
    return render(request, 'config/createProducto.html', context)




def editProducto(request, pk):
    product = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():

            try:
                form.save()
                message = "Producto editada correctamente."
                messages.success(request, message, extra_tags="edit")
            except ValidationError as e:
                messages.error(request, e.messages[0], extra_tags="error")
              
            return HttpResponseRedirect(reverse('listProducto'))
    else:
        form = ProductForm(instance=product)
    context = {
            'form': form,
            'title': 'Edición del Producto',
            'entity': 'Listado de productos',
            'action': 'edit',
       }

    return render(request, 'config/editProducto.html', context)
