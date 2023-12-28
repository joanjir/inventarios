from datetime import datetime

from django.forms import *
from inventario.models import UnidadMedida



class UnidadMForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['nombre'].widget.attrs['autofocus'] = True

    class Meta:
        model = UnidadMedida
        fields = '__all__'
        widgets = {
            'nombre': TextInput(
                attrs={
                    'placeholder': 'Ingrese un nombre',
                }
            ),
            }