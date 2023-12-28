from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import json
from django.db.models import  F

from inventario.models import Categoria, Producto, Compra, DetalleCompra, Venta


def compras(request):
    
    return render(request,'config/compras.html')

def list_compra(request):
    compra= Compra.objects.all()
    return render(request,'config/listCompra.html', {'compras': compra})

@csrf_exempt
@login_required
def buscar_producto(request):
    data = {}
    try:
        action = request.POST['action']
        if action == 'search_products':
            data = []  
            prods = Producto.objects.filter(name__icontains=request.POST['term'])[0:10]
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
            print( f'vents {vents}') # Imprime el contenido de vents           
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
                det = DetalleCompra(
                    compra=compra,
                    producto=prod,
                    cant=i['cant'],
                    precio=i['precio'],
                    costo=i['totalAmount'] # Save totalAmount to costo
                )
                detalles.append(det)
                prod.cant_dis += int(i['cant']) # Convert i['cant'] to int before adding                prod.save() # Guarda el producto
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
                
            # Obtener productos existentes y sus cantidades en la compra actual
            productos_existentes = {detalle.producto: detalle.cant for detalle in detalle_compra}
                
            
            vents = json.loads(request.POST['vents'])
            
            compraedit.fechaCompra = vents['fechaCompra']
            compraedit.fechaFactura = vents['fechaFactura']
            compraedit.numFactura = vents['numFactura']
            compraedit.total = vents['total']
            
            compraedit.save()
            nuevos_detalles = []
            for i in vents['products']:
                prod = Producto.objects.select_for_update().get(name=i['name'])
    
                if prod in productos_existentes:
                    # El producto existe en la compra actual
                    cant_anterior = productos_existentes[prod]
                    cant_actual = int(i['cant'])
        
                    if cant_actual < cant_anterior:
                        # La cantidad se ha reducido, resta la diferencia a cant_disponible
                        diferencia = cant_anterior - cant_actual
                        if prod.cant_dis >= diferencia:
                            prod.cant_dis -= diferencia
                        else:
                            # If the available quantity is less than the difference, set it to 0
                            prod.cant_dis = 0
                    elif cant_actual > cant_anterior:
                        # La cantidad ha aumentado, aumenta la diferencia a cant_disponible
                        diferencia = cant_actual - cant_anterior
                        prod.cant_dis += diferencia
                    prod.save()
        
                    # Actualizar el detalle existente
                    detalle_existente = DetalleCompra.objects.get(compra=compraedit, producto=prod)
                    detalle_existente.cant = cant_actual
                    detalle_existente.precio = i['precio']
                    detalle_existente.costo = i['costo']
                    detalle_existente.save()
                else:
                    # El producto es nuevo, aumenta cant_disponible
                    cant_actual = int(i['cant'])
                    prod.cant_dis += cant_actual
                    prod.save()
        
                    # Crea un nuevo detalle de compra
                    det = DetalleCompra(
                        compra=compraedit,
                        producto=prod,
                        cant=cant_actual,
                        precio=i['precio'],
                        costo=i['costo']
                    )
                    nuevos_detalles.append(det)
        
            DetalleCompra.objects.bulk_create(nuevos_detalles)
            
            # Eliminar detalles de compra que no están presentes en la solicitud
            productos_solicitud = [i['name'] for i in vents['products']]
            detalles_eliminar = detalle_compra.exclude(producto__name__in=productos_solicitud)
            for detalle_eliminar in detalles_eliminar:
                detalle_eliminar.producto.cant_dis -= detalle_eliminar.cant
                if detalle_eliminar.producto.cant_dis < 0:
                    detalle_eliminar.producto.cant_dis = 0
                detalle_eliminar.producto.save()
            detalles_eliminar.delete()
            
            data['success'] = True
            
    except Exception as e:
        data['error'] = str(e)
    
    return JsonResponse(data, safe=False)

@login_required
def eliminar_compra(request, compra_id):
    data = {}
    compra_id = request.session.get('compra_id')

    try:
        with transaction.atomic():
            compra = Compra.objects.select_for_update().get(id=compra_id)

            # Check if the purchase is already canceled
            if compra.estado == 'ANU':
                data['error'] = 'La compra ya está anulada.'
                return JsonResponse(data, safe=False)

            detalle_compra = DetalleCompra.objects.filter(compra=compra)

            for detalle in detalle_compra:
                prod = detalle.producto

                # # Check if the product quantity is already adjusted
                # if prod.cant_dis < detalle.cant:
                #     data['error'] = 'No se puede anular la compra. La cantidad disponible del producto "{}" es menor a la cantidad comprada.'.format(prod.name)
                #     return JsonResponse(data, safe=False)

                # # Check if the product is associated with any sales
                # if Venta.objects.filter(detalle_venta__producto=prod).exists():
                #     data['error'] = 'No se puede anular la compra. El producto "{}" ha sido vendido.'.format(prod.name)
                #     return JsonResponse(data, safe=False)

                prod.cant_dis -= detalle.cant
                prod.save()

            compra.estado = 'ANU'  # Marcar la compra como anulada
            compra.save()

            data['success'] = True
    except Exception as e:
        data['error'] = str(e)

    return JsonResponse(data, safe=False)

