from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from store.models import Order, CommissionLog, Product
from accounts.models import User, ResellerApplication
from django.db.models import Sum
from .forms import ProductForm, ResellerCreationForm

@login_required
def dashboard_home(request):
    user = request.user
    
    if user.is_owner():
        total_revenue = CommissionLog.objects.filter(user=user).aggregate(Sum('amount'))['amount__sum'] or 0.00
        total_orders = Order.objects.count()
        recent_orders = Order.objects.order_by('-created_at')[:5]
        resellers_count = User.objects.filter(role='RESELLER').count()
        pending_applications_count = ResellerApplication.objects.filter(status='PENDING').count()
        
        context = {
            'total_revenue': total_revenue,
            'total_orders': total_orders,
            'recent_orders': recent_orders,
            'resellers_count': resellers_count,
            'pending_applications_count': pending_applications_count,
            'role': 'Owner'
        }
        return render(request, 'dashboard/owner_home.html', context)
        
    elif user.is_reseller():
        total_commission = CommissionLog.objects.filter(user=user).aggregate(Sum('amount'))['amount__sum'] or 0.00
        my_sales = Order.objects.filter(reseller=user).count()
        downlines = user.downlines.all()
        recent_commissions = CommissionLog.objects.filter(user=user).order_by('-created_at')[:10]
        
        referral_link = f"{request.scheme}://{request.get_host()}/?ref={user.username}"
        
        # Get all products for link sharing
        all_products = Product.objects.all().order_by('-id')
        
        context = {
            'total_commission': total_commission,
            'my_sales': my_sales,
            'downlines': downlines,
            'recent_commissions': recent_commissions,
            'referral_link': referral_link,
            'all_products': all_products,
            'role': 'Reseller'
        }

        return render(request, 'dashboard/reseller_home.html', context)
        
    else:
        return redirect('store:home')

# --- OWNER ONLY VIEWS ---
def owner_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_owner():
            messages.error(request, 'Access denied. Owner only.')
            return redirect('dashboard:home')
        return view_func(request, *args, **kwargs)
    return wrapper

@owner_required
def product_list(request):
    products = Product.objects.all().order_by('-id')
    return render(request, 'dashboard/product_list.html', {'products': products})

@owner_required
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Produk berhasil ditambahkan.')
            return redirect('dashboard:products')
    else:
        form = ProductForm()
    return render(request, 'dashboard/product_form.html', {'form': form, 'title': 'Tambah Produk'})

@owner_required
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Produk berhasil diperbarui.')
            return redirect('dashboard:products')
    else:
        form = ProductForm(instance=product)
    return render(request, 'dashboard/product_form.html', {'form': form, 'title': 'Edit Produk', 'product': product})

@owner_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Produk berhasil dihapus.')
        return redirect('dashboard:products')
    return render(request, 'dashboard/product_confirm_delete.html', {'product': product})

@owner_required
def order_list(request):
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'dashboard/order_list.html', {'orders': orders})

from decimal import Decimal

@owner_required
def order_status_update(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            old_status = order.status
            order.status = new_status
            order.save()
            
            # If changing from PENDING to PAID, process commissions
            if old_status == 'PENDING' and new_status == 'PAID':
                # Process Owner Charge
                owner = User.objects.filter(role='OWNER').first()
                if not owner:
                    owner = User.objects.filter(is_superuser=True).first()
                    
                if owner:
                    owner.wallet_balance += order.platform_charge
                    owner.save()
                    CommissionLog.objects.create(
                        user=owner,
                        order=order,
                        amount=order.platform_charge,
                        description=f"Auto-charge 1% from Order #{order.id}"
                    )
                    
                # Process Reseller Commissions
                reseller = order.reseller
                if reseller:
                    # Tier 1
                    tier1_comm = order.total_price * Decimal('0.05')
                    reseller.wallet_balance += tier1_comm
                    reseller.save()
                    CommissionLog.objects.create(
                        user=reseller,
                        order=order,
                        amount=tier1_comm,
                        description=f"Direct Commission (5%) from Order #{order.id}"
                    )
                    
                    # Tier 2 (Upline)
                    if reseller.upline:
                        tier2_comm = order.total_price * Decimal('0.02')
                        upline = reseller.upline
                        upline.wallet_balance += tier2_comm
                        upline.save()
                        CommissionLog.objects.create(
                            user=upline,
                            order=order,
                            amount=tier2_comm,
                            description=f"Upline Commission (2%) from Order #{order.id} (via {reseller.username})"
                        )
            
            messages.success(request, f'Status pesanan #{order.id} berhasil diperbarui menjadi {new_status}.')
    return redirect('dashboard:orders')

@owner_required
def order_delete(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        order.delete()
        messages.success(request, f'Pesanan #{order.id} berhasil dihapus.')
    return redirect('dashboard:orders')

@owner_required
def reseller_list(request):
    resellers = User.objects.filter(role='RESELLER').order_by('-date_joined')
    return render(request, 'dashboard/reseller_list.html', {'resellers': resellers})
@owner_required
def reseller_create(request):
    if request.method == 'POST':
        form = ResellerCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Reseller baru berhasil didaftarkan.')
            return redirect('dashboard:resellers')
    else:
        form = ResellerCreationForm()
    return render(request, 'dashboard/reseller_form.html', {'form': form, 'title': 'Tambah Reseller'})

@owner_required
def reseller_applications(request):
    applications = ResellerApplication.objects.filter(status='PENDING').order_by('-created_at')
    return render(request, 'dashboard/reseller_applications.html', {'applications': applications})

@owner_required
def reseller_approve(request, pk):
    application = get_object_or_404(ResellerApplication, pk=pk, status='PENDING')
    if request.method == 'POST':
        application.status = 'APPROVED'
        application.save()
        
        user = application.user
        user.reseller_status = 'APPROVED'
        user.role = 'RESELLER'
        user.save()
        messages.success(request, f'Pengajuan reseller {user.username} berhasil disetujui.')
    return redirect('dashboard:reseller_applications')

@owner_required
def reseller_reject(request, pk):
    application = get_object_or_404(ResellerApplication, pk=pk, status='PENDING')
    if request.method == 'POST':
        application.status = 'REJECTED'
        application.save()
        
        user = application.user
        user.reseller_status = 'REJECTED'
        user.save()
        messages.success(request, f'Pengajuan reseller {user.username} ditolak.')
    return redirect('dashboard:reseller_applications')

from store.models import Withdrawal
from .forms import WithdrawalForm

@login_required
def reseller_withdraw(request):
    if not request.user.is_reseller():
        return redirect('dashboard:home')
        
    withdrawals = request.user.withdrawals.all().order_by('-created_at')
    
    if request.method == 'POST':
        form = WithdrawalForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            if amount < 50000:
                messages.error(request, 'Minimal penarikan adalah Rp 50.000')
            elif amount > request.user.wallet_balance:
                messages.error(request, 'Saldo wallet tidak mencukupi.')
            else:
                withdrawal = form.save(commit=False)
                withdrawal.user = request.user
                withdrawal.status = 'PENDING'
                
                # Potong saldo sekarang juga
                request.user.wallet_balance -= amount
                request.user.save()
                
                withdrawal.save()
                messages.success(request, 'Pengajuan penarikan komisi berhasil dikirim. Menunggu persetujuan Admin.')
                return redirect('dashboard:reseller_withdraw')
    else:
        form = WithdrawalForm()
        
    return render(request, 'dashboard/reseller_withdraw.html', {'form': form, 'withdrawals': withdrawals})

@owner_required
def owner_withdrawals(request):
    withdrawals = Withdrawal.objects.all().order_by('-created_at')
    return render(request, 'dashboard/owner_withdrawals.html', {'withdrawals': withdrawals})

@owner_required
def owner_withdrawal_approve(request, pk):
    withdrawal = get_object_or_404(Withdrawal, pk=pk, status='PENDING')
    if request.method == 'POST':
        withdrawal.status = 'APPROVED'
        withdrawal.save()
        messages.success(request, f'Penarikan #{withdrawal.id} disetujui.')
    return redirect('dashboard:owner_withdrawals')

@owner_required
def owner_withdrawal_reject(request, pk):
    withdrawal = get_object_or_404(Withdrawal, pk=pk, status='PENDING')
    if request.method == 'POST':
        withdrawal.status = 'REJECTED'
        withdrawal.save()
        
        # Refund the balance
        user = withdrawal.user
        user.wallet_balance += withdrawal.amount
        user.save()
        
        messages.success(request, f'Penarikan #{withdrawal.id} ditolak. Saldo dikembalikan.')
    return redirect('dashboard:owner_withdrawals')

@owner_required


def owner_inbox(request):
    from store.models import ContactMessage
    messages_list = ContactMessage.objects.all().order_by('-created_at')
    return render(request, 'dashboard/owner_inbox.html', {'messages_list': messages_list})

@owner_required
def owner_inbox_read(request, pk):
    from store.models import ContactMessage
    msg = get_object_or_404(ContactMessage, pk=pk)
    msg.is_read = True
    msg.save()
    return redirect('dashboard:owner_inbox')

@owner_required
def owner_inbox_reply(request, pk):
    from store.models import ContactMessage
    from django.utils import timezone
    msg = get_object_or_404(ContactMessage, pk=pk)
    if request.method == 'POST':
        reply = request.POST.get('reply')
        if reply:
            msg.admin_reply = reply
            msg.replied_at = timezone.now()
            msg.is_read = True
            msg.save()
            messages.success(request, 'Balasan berhasil dikirim.')
    return redirect('dashboard:owner_inbox')
