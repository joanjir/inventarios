from django import forms
from inventario.models import Empleado

class EmpleadoForm(forms.ModelForm):
    
    

    class Meta:
        model = Empleado
        fields = ['nombre', 'apellido', 'dni', 'telefono', 'imagen','direccion', 'puesto', 'fecha_contratacion', 'tipo_lugar', 'punto_venta', 'almacenes']
        widgets = {
            'fecha_contratacion': forms.DateInput(attrs={'class': 'datepicker'}),
        }

        def __init__(self, *args, **kwargs):
            super(EmpleadoForm, self).__init__(*args, **kwargs)
            self.fields['nombre'].required = True
            self.fields['apellido'].required = True
            self.fields['dni'].required = True
            self.fields['telefono'].required = True
            self.fields['direccion'].required = True