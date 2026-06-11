from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'stock', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full border border-gray-300 rounded py-2 px-3'}),
            'description': forms.Textarea(attrs={'class': 'w-full border border-gray-300 rounded py-2 px-3', 'rows': 4}),
            'price': forms.NumberInput(attrs={'class': 'w-full border border-gray-300 rounded py-2 px-3'}),
            'stock': forms.NumberInput(attrs={'class': 'w-full border border-gray-300 rounded py-2 px-3'}),
            'image': forms.ClearableFileInput(attrs={'class': 'w-full'}),
        }
