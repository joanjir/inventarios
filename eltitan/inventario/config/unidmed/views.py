from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import HttpResponseRedirect, HttpResponse, Http404, JsonResponse, HttpResponseForbidden
from django.urls import reverse

from inventario.models import UnidadMedida
from inventario.config.unidmed.forms import UnidadMForm


def listUnidadMedida(request):
    uns= UnidadMedida.objects.all()
    title = 'Unidades de medida'
    return render(request,'config/listUnidMed.html', {'uns' : uns, 'title': title})



def createUnidadMedida(request):
    if request.method == 'POST':
        form = UnidadMForm(request.POST)
        if form.is_valid():

            categoria = form.save(commit=False)
            
            categoria.save()

            message = "Categoría guardada correctamente."
            messages.success(request, message, extra_tags="create")

            return HttpResponseRedirect(reverse('listUnidadMedida'))
    else:
        form = UnidadMForm()
        context = {
           'form': form,
           'title': 'Creación de una Unidades de medida',
           'entity': 'Unidades de medida',
           'action': 'add'
       }
    return render(request, 'config/createUnidMed.html', context)