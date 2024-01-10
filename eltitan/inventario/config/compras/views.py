from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import json
from django.db.models import F
from decimal import Decimal


from inventario.models import Producto, Compra, DetalleCompra, Inventario, Almacen


def compras(request):

    return render(request, 'config/compras.html')


def list_compra(request):
    compra = Compra.objects.all()
    return render(request, 'config/listCompra.html', {'compras': compra})


@csrf_exempt
@login_required
def buscar_producto(request):
    data = {}
    try:
        action = request.POST['action']
        if action == 'search_products':
            data = []
            prods = Producto.objects.filter(
                name__icontains=request.POST['term'])[0:10]
            for i in prods:
                item = i.toJSON()
                item['text'] = i.name
                data.append(item)
                print(f'busqueda de articulos {data}')

        else:
            data['error'] = 'No ha ingresado a ninguna opción'
    except Exception as e:
        data['error'] = str(e)
    return JsonResponse(data, safe=False)


@csrf_protect
@login_required
def guardar_compra(request):
    data = {}
    try:
        with transaction.atomic():
            vents = json.loads(request.POST.get('vents', '{}'))
            print(f'vents {vents}')  # Imprime el contenido de vents
            compra = Compra(
                fechaCompra=vents['fechaCompra'],
                numFactura=vents['numFactura'],
                fechaFactura=vents['fechaFactura'],
                total=float(vents['total'])
            )
            compra.save()

            detalles = []
            for i in vents['products']:
                prod = Producto.objects.select_for_update().get(name=i['name'])
                central_warehouse = Almacen.objects.get(central=True)
                inv_item, created = Inventario.objects.get_or_create(
                    producto=prod, almacen=central_warehouse)
                if created:
                    inv_item.cantidad = Decimal(i['cant'])
                else:
                    inv_item.cantidad += Decimal(i['cant'])
                inv_item.save()

                det = DetalleCompra(
                    compra=compra,
                    producto=prod,
                    cant=i['cant'],
                    precio=i['precio'],
                    costo=i['totalAmount']  # Save totalAmount to costo
                )
                detalles.append(det)
                # Convert i['cant'] to Decimal before adding
                prod.cant_dis += Decimal(i['cant'])
                prod.save()
            DetalleCompra.objects.bulk_create(detalles)
            data['action'] = 'add'

    except Exception as e:
        data['error'] = str(e)
    return JsonResponse(data, safe=False)


@csrf_protect
@login_required
def editar_compra(request, compra_id):
    compra = Compra.objects.get(id=compra_id)
    request.session['compra_id'] = compra_id
    return render(request, 'config/editCompras.html', {'compra': compra})


@csrf_protect
@login_required
def editar(request):
    data = {}
    try:
        compra_id = request.session.get('compra_id')
        with transaction.atomic():
            compraedit = Compra.objects.select_for_update().get(id=compra_id)

            data = {
                'fechaCompra': compraedit.fechaCompra,
                'fechaFactura': compraedit.fechaFactura,
                'numFactura': compraedit.numFactura,
                'total': compraedit.total,
            }

            detalle_compra = DetalleCompra.objects.filter(compra=compraedit)
            data['detalles'] = []

            for detalle in detalle_compra:
                detalle_data = {
                    'name': detalle.producto.name,
                    'cant': int(detalle.cant),
                    'precio': detalle.precio,
                    'costo': detalle.costo
                }
                data['detalles'].append(detalle_data)

            productos_existentes = {
                detalle.producto: detalle.cant for detalle in detalle_compra}

            vents = json.loads(request.POST['vents'])

            compraedit.fechaCompra = vents['fechaCompra']
            compraedit.fechaFactura = vents['fechaFactura']
            compraedit.numFactura = vents['numFactura']
            compraedit.total = vents['total']

            compraedit.save()
            nuevos_detalles = []
            central_warehouse = Almacen.objects.get(central=True)
            for i in vents['products']:
                prod = Producto.objects.select_for_update().get(name=i['name'])
                inv_item, created = Inventario.objects.get_or_create(
                    producto=prod, almacen=central_warehouse)

                if prod in productos_existentes:
                    cant_anterior = productos_existentes[prod]
                    cant_actual = int(i['cant'])

                    if cant_actual < cant_anterior:
                        diferencia = cant_anterior - cant_actual
                        if inv_item.cantidad >= diferencia:
                            inv_item.cantidad -= diferencia
                        else:
                            inv_item.cantidad = 0
                        prod.cant_dis -= diferencia
                    elif cant_actual > cant_anterior:
                        diferencia = cant_actual - cant_anterior
                        inv_item.cantidad += diferencia
                        prod.cant_dis += diferencia
                    inv_item.save()
                    prod.save()

                    detalle_existente = DetalleCompra.objects.get(
                        compra=compraedit, producto=prod)
                    detalle_existente.cant = cant_actual
                    detalle_existente.precio = i['precio']
                    detalle_existente.costo = i['costo']
                    detalle_existente.save()
                else:
                    cant_actual = int(i['cant'])
                    inv_item.cantidad += cant_actual
                    inv_item.save()
                    prod.cant_dis += cant_actual
                    prod.save()

                    det = DetalleCompra(
                        compra=compraedit,
                        producto=prod,
                        cant=cant_actual,
                        precio=i['precio'],
                        costo=i['costo']
                    )
                    nuevos_detalles.append(det)

            DetalleCompra.objects.bulk_create(nuevos_detalles)

            productos_solicitud = [i['name'] for i in vents['products']]
            detalles_eliminar = detalle_compra.exclude(
                producto__name__in=productos_solicitud)
            for detalle_eliminar in detalles_eliminar:
                inv_item = Inventario.objects.get(
                    producto=detalle_eliminar.producto, almacen=central_warehouse)
                if inv_item.cantidad >= detalle_eliminar.cant:
                    inv_item.cantidad -= detalle_eliminar.cant
                else:
                    inv_item.cantidad = 0
                inv_item.save()
                detalle_eliminar.producto.cant_dis -= detalle_eliminar.cant
                detalle_eliminar.producto.save()
            detalles_eliminar.delete()

            data['success'] = True

    except Exception as e:
        data['error'] = str(e)

    return JsonResponse(data, safe=False)


@login_required
def eliminar_compra(request, compra_id):
    try:
        with transaction.atomic():
            compra = Compra.objects.select_for_update().get(id=compra_id)

            if compra.estado == 'ANU':
                return JsonResponse({'error': 'La compra ya está anulada.'}, safe=False)

            detalle_compra = DetalleCompra.objects.filter(compra=compra)

            central_warehouse = Almacen.objects.get(central=True)

            for detalle in detalle_compra:
                prod = detalle.producto
                inv_item, created = Inventario.objects.get_or_create(
                    producto=prod, almacen=central_warehouse)

                if created:
                    inv_item.cantidad = 0

                inv_item.cantidad -= detalle.cant
                inv_item.save()

                if inv_item.cantidad <= 0:
                    inv_item.delete()

                prod.cant_dis -= detalle.cant
                prod.save()

            compra.estado = 'ANU'
            compra.save()

            return JsonResponse({'success': True}, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, safe=False)
    
