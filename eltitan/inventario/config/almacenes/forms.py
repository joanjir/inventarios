from django import forms
from inventario.models import Almacen


class AlmacenForm(forms.ModelForm):
   class Meta:
       model = Almacen
       fields = ['nombre', 'ubicacion', 'activo', 'central']

   def __init__(self, *args, **kwargs):
       super().__init__(*args, **kwargs)
       if Almacen.objects.filter(central=True).exists():
           self.fields['central'].disabled = True

   def clean_central(self):
       central = self.cleaned_data.get('central')
       if self.instance and self.instance.pk:
           # If this form is for an existing object, keep the original 'central' value
           return self.instance.central
       return central
