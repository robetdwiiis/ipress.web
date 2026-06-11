from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, Order, CommissionLog
from accounts.models import User, ResellerApplication
from accounts.forms import ResellerApplicationForm
from decimal import Decimal

def home_view(request):
    ref = request.GET.get('ref')
    if ref:
        request.session['ref'] = ref
        
    products = Product.objects.all()
    return render(request, 'store/home.html', {'products': products})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'store/product_detail.html', {'product': product})

@login_required
def my_orders(request):
    orders = Order.objects.filter(buyer=request.user).order_by('-created_at')
    return render(request, 'store/my_orders.html', {'orders': orders})

@login_required
def apply_reseller_view(request):
    if request.user.reseller_status == 'APPROVED' or request.user.role == 'RESELLER':
        messages.info(request, 'Anda sudah menjadi reseller.')
        return redirect('store:reseller_program')
        
    if request.user.reseller_status == 'PENDING':
        messages.info(request, 'Pengajuan reseller Anda sedang diproses.')
        return redirect('store:reseller_program')

    if request.method == 'POST':
        form = ResellerApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user
            application.status = 'PENDING'
            application.save()
            
            request.user.reseller_status = 'PENDING'
            request.user.save()
            
            messages.success(request, 'Pengajuan reseller berhasil dikirim! Admin akan segera meninjau detail Anda.')
            return redirect('store:reseller_program')
    else:
        form = ResellerApplicationForm()
        
    return render(request, 'store/apply_reseller_form.html', {'form': form})

def reseller_program(request):
    return render(request, 'store/reseller_program.html')

def about_view(request):
    return render(request, 'store/about.html')

def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message_text = request.POST.get('message')
        
        from .models import ContactMessage
        ContactMessage.objects.create(
            name=name,
            email=email,
            subject=subject,
            message=message_text,
            user=request.user if request.user.is_authenticated else None
        )
        
        messages.success(request, f'Terima kasih {name}! Pesan Anda telah diterima. Kami akan merespons ke {email} dalam 1x24 jam.')
        return redirect('store:contact')
        
    history = None
    if request.user.is_authenticated:
        from .models import ContactMessage
        history = ContactMessage.objects.filter(user=request.user).order_by('-created_at')
        
    return render(request, 'store/contact.html', {'history': history})

@login_required
def checkout_view(request, pk):

        
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        payment_method = request.POST.get('payment_method', 'BANK_BCA')
        shipping_name = request.POST.get('shipping_name', request.user.get_display_name())
        shipping_phone = request.POST.get('shipping_phone', request.user.phone_number)
        shipping_address = request.POST.get('shipping_address', request.user.address)
        
        # Calculate pricing
        base_price = product.price
        total_price = base_price * quantity
        platform_charge = total_price * Decimal('0.01')
        
        # Find reseller
        ref_username = request.session.get('ref')
        reseller = None
        if ref_username:
            try:
                reseller = User.objects.get(username=ref_username, role='RESELLER')
            except User.DoesNotExist:
                pass
                
        # Create Order
        order = Order.objects.create(
            buyer=request.user,
            product=product,
            quantity=quantity,
            base_price=base_price,
            total_price=total_price,
            platform_charge=platform_charge,
            reseller=reseller,
            payment_method=payment_method,
            shipping_name=shipping_name,
            shipping_phone=shipping_phone,
            shipping_address=shipping_address,
            status='PENDING'
        )
                
        # Deduct Stock
        product.stock -= quantity
        product.save()
            
        messages.success(request, f"Pesanan berhasil dibuat! Silakan lakukan pembayaran sesuai metode yang dipilih.")
        return redirect('store:order_detail', pk=order.pk)
        
    return render(request, 'store/checkout.html', {'product': product})

@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk, buyer=request.user)
    
    # Payment info per method
    payment_info = {
        'BANK_BCA': {'name': 'Bank BCA', 'number': '1234567890', 'account': 'iPremium Store', 'icon': 'fa-university'},
        'BANK_BRI': {'name': 'Bank BRI', 'number': '0987654321', 'account': 'iPremium Store', 'icon': 'fa-university'},
        'BANK_MANDIRI': {'name': 'Bank Mandiri', 'number': '1122334455', 'account': 'iPremium Store', 'icon': 'fa-university'},
        'QRIS': {'name': 'QRIS', 'number': None, 'account': 'Scan QR di bawah ini', 'icon': 'fa-qrcode'},
    }
    payment = payment_info.get(order.payment_method, payment_info['BANK_BCA'])
    return render(request, 'store/order_detail.html', {'order': order, 'payment': payment})

@login_required
def cancel_order(request, pk):
    order = get_object_or_404(Order, pk=pk, buyer=request.user)
    
    if order.status == 'PENDING':
        product = order.product
        product.stock += order.quantity
        product.save()
        order.delete()
        messages.success(request, 'Pesanan berhasil dibatalkan.')
    else:
        messages.error(request, 'Hanya pesanan dengan status Menunggu Pembayaran yang dapat dibatalkan.')
        
    return redirect('store:my_orders')

@login_required
def upload_payment_proof(request, pk):
    order = get_object_or_404(Order, pk=pk, buyer=request.user)
    
    if order.status != 'PENDING':
        messages.error(request, 'Bukti pembayaran hanya bisa diunggah untuk pesanan yang menunggu pembayaran.')
        return redirect('store:order_detail', pk=pk)
    
    if request.method == 'POST' and request.FILES.get('payment_proof'):
        order.payment_proof = request.FILES['payment_proof']
        order.save()
        messages.success(request, 'Bukti pembayaran berhasil diunggah! Admin akan memverifikasi dalam 1×24 jam.')
    else:
        messages.error(request, 'Silakan pilih file gambar terlebih dahulu.')
    
    return redirect('store:order_detail', pk=pk)
