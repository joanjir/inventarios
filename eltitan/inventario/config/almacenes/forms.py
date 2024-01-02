from django import forms
from inventario.models import Almacen

class AlmacenForm(forms.ModelForm):
    class Meta:
        model = Almacen
        fields = ['nombre', 'ubicacion', 'activo', 'central']
        

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Comprueba si ya existe un almacén central
        if Almacen.objects.filter(central=True).exists():
            # Elimina el campo central si ya existe un almacén central
            del self.fields['central']