from datetime import datetime

from django.forms import *
from inventario.models import PuntoVenta



class PuntoVentaForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['nombre'].widget.attrs['autofocus'] = True

    class Meta:
        model = PuntoVenta
        fields = '__all__'
        widgets = {
            'nombre': TextInput(
                attrs={
                    'placeholder': 'Ingrese un nombre',
                }
            ),
            'ubicacion': Textarea(
                attrs={
                    'placeholder': 'Ingrese una ubicacion',
                    'rows': 3,
                    'cols': 3
                }
            ),
        }