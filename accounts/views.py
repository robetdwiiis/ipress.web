from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm, UserProfileForm
from .models import User

def register_view(request):
    # Check for referral in URL (e.g. ?ref=username)
    ref_username = request.GET.get('ref')
    upline = None
    if ref_username:
        try:
            upline = User.objects.get(username=ref_username, role='RESELLER')
        except User.DoesNotExist:
            pass

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'BUYER'
            if upline:
                user.upline = upline
            user.save()
            login(request, user)
            messages.success(request, 'Registration successful.')
            return redirect('store:home')
    else:
        form = CustomUserCreationForm()
        
    return render(request, 'accounts/register.html', {'form': form, 'upline': upline})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                if user.is_owner() or user.is_reseller():
                    return redirect('dashboard:home')
                return redirect('store:home')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, 'You have successfully logged out.')
    return redirect('store:home')

@login_required
def profile_view(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil Anda berhasil diperbarui.')
            return redirect('accounts:profile')
        else:
            print("Profile Form Errors:", form.errors)
            messages.error(request, 'Terjadi kesalahan saat memperbarui profil.')
    else:
        form = UserProfileForm(instance=request.user)
    
    # Get user orders for "shopee-like" history
    from store.models import Order
    orders = Order.objects.filter(buyer=request.user).order_by('-created_at')
    
    return render(request, 'accounts/profile.html', {'form': form, 'orders': orders})

@login_required
def password_change_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Password Anda berhasil diperbarui.')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Silakan perbaiki kesalahan di bawah ini.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'accounts/password_change.html', {'form': form})

@login_required
def apply_reseller(request):
    if request.method == 'POST':
        if request.user.reseller_status in ['NONE', 'REJECTED']:
            request.user.reseller_status = 'PENDING'
            request.user.save()
            messages.success(request, 'Pengajuan reseller Anda telah dikirim dan sedang menunggu persetujuan admin.')
        else:
            messages.info(request, 'Anda sudah memiliki pengajuan yang aktif atau sudah menjadi reseller.')
    return redirect('accounts:profile')

