from django.shortcuts import render, redirect
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
