from django import forms
from store.models import Product, Withdrawal
from accounts.models import User
from django.conf import settings

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'stock', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full p-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition'}),
            'description': forms.Textarea(attrs={'class': 'w-full p-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition', 'rows': 4}),
            'price': forms.NumberInput(attrs={'class': 'w-full p-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition'}),
            'stock': forms.NumberInput(attrs={'class': 'w-full p-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition'}),
            'image': forms.FileInput(attrs={'class': 'w-full p-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition'}),
        }

class ResellerCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'w-full p-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition'}))
    
    class Meta:
        model = User
        fields = ['username', 'email', 'upline']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'w-full p-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition'}),
            'email': forms.EmailInput(attrs={'class': 'w-full p-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition'}),
            'upline': forms.Select(attrs={'class': 'w-full p-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from accounts.models import User
        self.fields['upline'].queryset = User.objects.filter(role='RESELLER')
        self.fields['upline'].required = False

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.role = 'RESELLER'
        if commit:
            user.save()
        return user

class WithdrawalForm(forms.ModelForm):
    class Meta:
        model = Withdrawal
        fields = ['amount', 'bank_name', 'account_number', 'account_name']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'w-full rounded-xl border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500', 'min': '50000'}),
            'bank_name': forms.Select(choices=[('BANK_BRI', 'Bank BRI'), ('BANK_BNI', 'Bank BNI'), ('BANK_MANDIRI', 'Bank Mandiri'), ('DANA', 'DANA'), ('OVO', 'OVO'), ('GOPAY', 'GoPay')], attrs={'class': 'w-full rounded-xl border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'}),
            'account_number': forms.TextInput(attrs={'class': 'w-full rounded-xl border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500', 'placeholder': 'Misal: 0123456789'}),
            'account_name': forms.TextInput(attrs={'class': 'w-full rounded-xl border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500', 'placeholder': 'Nama sesuai rekening/ewallet'}),
        }
        labels = {
            'amount': 'Jumlah Penarikan (Rp)',
            'bank_name': 'Bank / E-Wallet',
            'account_number': 'Nomor Rekening / No. HP',
            'account_name': 'Nama Pemilik',
        }
