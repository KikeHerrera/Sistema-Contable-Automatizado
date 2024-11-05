from django import forms
from django.core.exceptions import ValidationError
from Sistema.models import Transaccion, Asiento, CuentaContable
from datetime import date
from .models import Empleado


class TransaccionForm(forms.ModelForm):
    fecha_operacion = forms.DateField(
        initial=date.today,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label="Fecha Operación"
    )

    class Meta:
        model = Transaccion
        fields = ['fecha_operacion', 'contenido']
        widgets = {
            'contenido': forms.Textarea(attrs={'class': 'form-control'}),
        }


class AsientoCustomForm(forms.Form):
    cuenta_deudor = forms.ModelChoiceField(
        queryset=CuentaContable.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Cuenta Deudor"
    )
    

    cuenta_acreedor = forms.ModelChoiceField(
        queryset=CuentaContable.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Cuenta Acreedor"
    )

    monto = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
        label="Monto"
    )
    
    cargar_iva = forms.ModelChoiceField(
        queryset=CuentaContable.objects.filter(codigo_cuenta__in=['1.1.6', '2.1.3']),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Cargar IVA 13%",
        empty_label="No Aplica",
        required=False 
    )

    def clean_monto(self):
        monto = self.cleaned_data.get('monto')
        if monto <= 0:
            raise ValidationError('El monto debe ser mayor a cero.')
        return monto
    

class EmpleadoForm(forms.ModelForm):
    class Meta:
            model = Empleado
            fields = ['nombre', 'salario_nominal_diario', 'dias_semanales']
            widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'salario_nominal_diario': forms.NumberInput(attrs={'class': 'form-control'}),
            'dias_semanales': forms.NumberInput(attrs={'class': 'form-control'}),
        }
