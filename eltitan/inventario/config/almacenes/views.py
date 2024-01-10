from django.shortcuts import render, redirect, get_object_or_404
from inventario.models import Almacen
from .forms import AlmacenForm

def create_almacen(request):
   if request.method == 'POST':
       form = AlmacenForm(request.POST)
       if form.is_valid():
           form.save()
           return redirect('list_almacen')
   else:
       form = AlmacenForm()
   return render(request, 'config/crearAlmacen.html', {'form': form})


def list_almacen(request):
    alm = Almacen.objects.all()
    title = 'Listado de Almacenes'
    return render(request,'config/listarAlmacen.html', {'alms' : alm, 'title': title})


def edit_almacen(request, almacen_id):
   almacen = get_object_or_404(Almacen, id=almacen_id)
   if request.method == 'POST':
       form = AlmacenForm(request.POST, instance=almacen)
       if form.is_valid():
           form.save()
           return redirect('list_almacen')
   else:
       form = AlmacenForm(instance=almacen)
   return render(request, 'config/editAlmacen.html', {'form': form})