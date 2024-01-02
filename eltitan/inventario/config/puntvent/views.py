from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import HttpResponseRedirect, HttpResponse, Http404, JsonResponse, HttpResponseForbidden
from django.urls import reverse
from django.core.exceptions import ValidationError


from inventario.models import PuntoVenta
from .forms import PuntoVentaForm



def list_puntvemt(request):
    ptnv = PuntoVenta.objects.all()
    title = 'Puntos de ventas'
    return render(request,'config/listpuntVenta.html', {'ptnvs' : ptnv, 'title': title})



def create_puntvemt(request):
    if request.method == 'POST':
        form = PuntoVentaForm(request.POST)
        if form.is_valid():

            categoria = form.save(commit=False)
            
            categoria.save()

            message = "Punto de Venta guardada correctamente."
            messages.success(request, message, extra_tags="create")

            return HttpResponseRedirect(reverse('list_puntvemt'))
    else:
        form = PuntoVentaForm()
        context = {
           'form': form,
           'title': 'Creación de un Punto de Venta',
           'entity': 'Puntos de ventas',
           'action': 'add'
       }
    return render(request, 'config/createpuntVenta.html', context)



