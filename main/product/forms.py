from django import forms
from .models import Product

class ProductAdminForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'
        widgets = {
            'year': forms.NumberInput(attrs={
                'min': 1970,  # Можно задать минимальный год
                'max': 2050,  # Можно задать максимальный год
                'placeholder': 'Введите год выпуска'
            }),
        }