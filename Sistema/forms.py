from django import forms
from django.core.exceptions import ValidationError
from Sistema.models import Transaccion, Asiento, CuentaContable
from datetime import date


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

    def clean_monto(self):
        monto = self.cleaned_data.get('monto')
        if monto <= 0:
            raise ValidationError('El monto debe ser mayor a cero.')
        return monto
