from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from inventario.models import Empleado
from django.db.models import Q
from .forms import EmpleadoForm

def empleado_create(request):
    if request.method == 'POST':
        form = EmpleadoForm(request.POST, request.FILES)
        if form.is_valid():
            empleado = form.save(commit=False)
            telefono_prefijo = request.POST.get('telefono_prefijo')  # Obtener el valor del prefijo del campo oculto
            numero_telefono = form.cleaned_data['telefono']  # Obtener el número de teléfono del formulario
            empleado.telefono = f'{telefono_prefijo}{numero_telefono}'  # Concatenar el prefijo y el número
            empleado.save()
            return redirect('empleado_list')
    else:
        form = EmpleadoForm()
    
    context = {
        'form': form,
        'title': 'Agregar un Empleado',
        'entity': 'Listado de empleados',
        'action': 'add',
    }
    return render(request, 'config/Empleadocreate.html', context)


def empleado_list(request):
    nombre = request.GET.get('nombre')
    apellido = request.GET.get('apellido')
    dni = request.GET.get('dni')
    telefono = request.GET.get('telefono')

    empleados = Empleado.objects.all()

    if nombre:
        empleados = empleados.filter(nombre__icontains=nombre)
    if apellido:
        empleados = empleados.filter(apellido__icontains=apellido)
    if dni:
        empleados = empleados.filter(dni=dni)
    if telefono:
        empleados = empleados.filter(telefono=telefono)

    paginator = Paginator(empleados, 4)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'config/Empleadolist.html', {'page_obj': page_obj})

@csrf_exempt
@require_POST
def eliminar_empleado(request, empleado_id):
    empleado = Empleado.objects.get(id=empleado_id)
    # Realiza cualquier lógica adicional antes de eliminar al empleado, si es necesario
    empleado.delete()
    return redirect('empleado_list')

