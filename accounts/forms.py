from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, ResellerApplication

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email', 'phone_number', 'address', 'city')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'w-full p-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-blue-500 outline-none'}),
            'first_name': forms.TextInput(attrs={'class': 'w-full p-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-blue-500 outline-none'}),
            'last_name': forms.TextInput(attrs={'class': 'w-full p-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-blue-500 outline-none'}),
            'email': forms.EmailInput(attrs={'class': 'w-full p-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-blue-500 outline-none'}),
            'phone_number': forms.TextInput(attrs={'class': 'w-full p-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-blue-500 outline-none', 'placeholder': 'Contoh: 08123456789'}),
            'address': forms.Textarea(attrs={'class': 'w-full p-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-blue-500 outline-none', 'rows': 2}),
            'city': forms.TextInput(attrs={'class': 'w-full p-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-blue-500 outline-none'}),
        }

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone_number', 'address', 'city', 'postal_code', 'profile_picture', 'bank_name', 'account_number']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'w-full p-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-blue-500 outline-none'}),
            'first_name': forms.TextInput(attrs={'class': 'w-full p-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-blue-500 outline-none'}),
            'last_name': forms.TextInput(attrs={'class': 'w-full p-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-blue-500 outline-none'}),
            'email': forms.EmailInput(attrs={'class': 'w-full p-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-blue-500 outline-none'}),
            'phone_number': forms.TextInput(attrs={'class': 'w-full p-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-blue-500 outline-none', 'placeholder': 'Contoh: 08123456789'}),
            'address': forms.Textarea(attrs={'class': 'w-full p-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-blue-500 outline-none', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'w-full p-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-blue-500 outline-none'}),
            'postal_code': forms.TextInput(attrs={'class': 'w-full p-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-blue-500 outline-none'}),
            'bank_name': forms.TextInput(attrs={'class': 'w-full p-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-blue-500 outline-none', 'placeholder': 'Contoh: BCA / Mandiri'}),
            'account_number': forms.TextInput(attrs={'class': 'w-full p-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-blue-500 outline-none', 'placeholder': 'Contoh: 1234567890'}),
        }

class ResellerApplicationForm(forms.ModelForm):
    class Meta:
        model = ResellerApplication
        fields = ['social_media_link', 'marketing_plan']
        widgets = {
            'social_media_link': forms.URLInput(attrs={'class': 'w-full p-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-blue-500 outline-none', 'placeholder': 'https://instagram.com/tokoanda'}),
            'marketing_plan': forms.Textarea(attrs={'class': 'w-full p-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-blue-500 outline-none', 'rows': 4, 'placeholder': 'Ceritakan strategi Anda menjual produk iPhone kami (misal: lewat IG Ads, broadcast WhatsApp, dsb).'}),
        }
