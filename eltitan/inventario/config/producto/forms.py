from datetime import datetime

from django.forms import *
from inventario.models import Producto, Categoria, UnidadMedida



class ProductForm(ModelForm):
   
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['autofocus'] = True

        self.fields['cat'].queryset = Categoria.objects.filter(activo=True)
        self.fields['unidad_medida'].queryset = UnidadMedida.objects.filter(activo=True)
        
    class Meta:
        model = Producto
        fields = ['name', 'cat', 'precio_venta','precio_venta_m','unidad_medida','activo']
        widgets = {
           'name': TextInput(
               attrs={
                  'placeholder': 'Ingrese un nombre',
               }
           ),
           'cat': Select(
               attrs={
                  'class': 'select2',
                  'style': 'width: 100%'
               }
           ),
           'unidad_medida': Select(
               attrs={
                  'class': 'select2',
                  'style': 'width: 100%'
               }
           ),
           'precio_venta': TextInput(attrs={
               'class': 'form-control',
           }),
       }

    def save(self, commit=True):
        instance = super(ProductForm, self).save(commit=False)
        if commit:
            instance.save()
        return instance

    

