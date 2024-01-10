from django.shortcuts import render, redirect


def crear_movimiento(request):
    if request.method == 'POST':
        form = MovimientoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('ruta_despues_de_guardar')
    else:
        form = MovimientoForm()
    return render(request, 'config/movimiento.html', {'form': form})
