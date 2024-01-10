from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect, HttpResponse, Http404, JsonResponse, HttpResponseForbidden
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from django.forms.models import model_to_dict
from django.utils import timezone
from decimal import InvalidOperation
import datetime
from inventario.models import Almacen, PuntoVenta, Inventario, Producto, Movimiento, OrigenDestino


from django.core.paginator import Paginator


def get_inventory_by_almacen(request):
    # Initialize an empty dictionary to hold the inventory for each Almacen
    inventory_by_almacen = {}

    # Get all Almacens
    almacens = Almacen.objects.all()
    for almacen in almacens:

        # Add the inventory to the dictionary using the almacen id as the key
        inventory_by_almacen[str(almacen.id)] = {
            'id': almacen.id,
            'name': almacen.nombre,
            'ubicacion': almacen.ubicacion,
            'activo': almacen.activo,
            'central': almacen.central,
        }

    # Convert dict_values to a list and pass it to the Paginator
    inventory_list = list(inventory_by_almacen.values())
    paginator = Paginator(inventory_list, 3)  # Show 10 inventories per page

    # Get the page number from the request
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Pass the page object to the template
    return render(request, 'config/inventarioalm.html', {'page_obj': page_obj})


def get_inventory_by_punto_venta(request):
    # Initialize an empty dictionary to hold the inventory for each PuntoVenta
    inventory_by_punto_venta = {}

    # Get all PuntosVenta
    puntos_venta = PuntoVenta.objects.all()
    for punto_venta in puntos_venta:

        # Add the inventory to the dictionary using the punto_venta id as the key
        inventory_by_punto_venta[str(punto_venta.id)] = {
            'id': punto_venta.id,

            'name': punto_venta.nombre,
            'ubicacion': punto_venta.ubicacion,
            'activo': punto_venta.activo,
        }

    # Convert dict_values to a list and pass it to the Paginator
    inventory_list = list(inventory_by_punto_venta.values())
    paginator = Paginator(inventory_list, 3)  # Show 10 inventories per page

    # Get the page number from the request
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Pass the page object to the template
    return render(request, 'config/inventariopv.html', {'page_obj': page_obj})


def inventory_detail_warehouse(request, almacen_id):
    # Obtén el almacén con el id dado
    almacen = get_object_or_404(Almacen, id=almacen_id)

    # Obtén el inventario para el almacén actual
    inventario = Inventario.objects.filter(almacen=almacen)

    # Obtén todos los Almacen y PuntoVenta
    almacens = Almacen.objects.all()
    puntos_venta = PuntoVenta.objects.all()

    # Crea un OrigenDestino para cada Almacen y PuntoVenta
    origins_destinies = []
    for almacen in almacens:
        origen_destino = OrigenDestino.objects.get(almacen=almacen)
        origins_destinies.append(origen_destino)
    for punto_venta in puntos_venta:
        origen_destino = OrigenDestino.objects.get(punto_venta=punto_venta)
        origins_destinies.append(origen_destino)

    print(origins_destinies)
    # Pasa el inventario y los OrigenDestino a la plantilla
    return render(request, 'config/inventory_detail.html', {'inventory': inventario, 'origins_destinies': origins_destinies})


def inventory_detail_store(request, store_id):
    # Obtén el almacén con el id dado
    punto_venta = get_object_or_404(PuntoVenta, id=store_id)

    # Obtén el inventario para el almacén actual
    inventario = Inventario.objects.filter(punto_venta=punto_venta)

    # Obtén todos los Almacen y PuntoVenta
    almacens = Almacen.objects.all()
    puntos_venta = PuntoVenta.objects.all()

    # Crea un OrigenDestino para cada Almacen y PuntoVenta
    origins_destinies = []
    for almacen in almacens:
        origen_destino = OrigenDestino.objects.get(almacen=almacen)
        origins_destinies.append(origen_destino)
    for punto_venta in puntos_venta:
        origen_destino = OrigenDestino.objects.get(punto_venta=punto_venta)
        origins_destinies.append(origen_destino)

    print(origins_destinies)
    # Pasa el inventario y los OrigenDestino a la plantilla
    return render(request, 'config/inventory_detail_stores.html', {'inventory': inventario, 'origins_destinies': origins_destinies})


def mover_inventario(request, inventario_id):
    if request.method == 'POST':
        # Get the original inventory
        inventario_origen = get_object_or_404(Inventario, id=inventario_id)

        # Get the OrigenDestino of origin
        if inventario_origen.almacen:
            origen = OrigenDestino.objects.get(
                almacen=inventario_origen.almacen)
        elif inventario_origen.punto_venta:
            origen = OrigenDestino.objects.get(
                punto_venta=inventario_origen.punto_venta)
        else:
            return JsonResponse({'detail': 'No se encontró un almacén ni un punto de venta para este inventario.'}, status=404)

        # Get the OrigenDestino of destination
        destino = OrigenDestino.objects.get(id=request.POST['destino'])

        # Check if the origin and destination are the same
        if origen == destino:
            return JsonResponse({'detail': 'El origen y el destino no pueden ser el mismo.'}, status=400)

        # Get the requested quantity
        cantidad_solicitada = request.POST.get('cantidad')

        if not cantidad_solicitada:
            return JsonResponse({'detail': 'La cantidad solicitada no puede estar vacía.'}, status=400)
        else:
            try:
                cantidad_solicitada = Decimal(cantidad_solicitada)
            except InvalidOperation:
                return JsonResponse({'detail': 'La cantidad solicitada debe ser un número válido.'}, status=400)
        # Create a new movement
        movimiento = Movimiento(
            producto=inventario_origen.producto,
            cantidad=request.POST['cantidad'],
            origen=origen,
            destino=destino,
            fecha=timezone.now()
        )
        movimiento.save()

        # Update the quantity of product in the original inventory
        inventario_origen.cantidad -= Decimal(request.POST['cantidad'])
        inventario_origen.save()

        # Check if the quantity has reached zero
        if inventario_origen.cantidad == 0:
            # Delete the inventory item
            inventario_origen.delete()

        # Get the inventory of destination
        if destino.almacen:
            inventario_destino, created = Inventario.objects.get_or_create(
                producto=inventario_origen.producto, almacen=destino.almacen)
        elif destino.punto_venta:
            inventario_destino, created = Inventario.objects.get_or_create(
                producto=inventario_origen.producto, punto_venta=destino.punto_venta)

        if not inventario_destino:
            inventario_destino = Inventario(producto=inventario_origen.producto, almacen=destino.almacen if destino.almacen else None,
                                            punto_venta=destino.punto_venta if destino.punto_venta else None, cantidad=0)

        # Update the quantity of product in the destination inventory
        inventario_destino.cantidad += Decimal(request.POST['cantidad'])
        inventario_destino.save()

        return JsonResponse({'status': 'ok'})
    else:
        return JsonResponse({'detail': 'La solicitud debe ser un POST.'}, status=400)
