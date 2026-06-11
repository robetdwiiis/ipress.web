from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    
    def __str__(self):
        return self.name

class Order(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Menunggu'),
        ('PAID', 'Disetujui & Dibayar'),
        ('SHIPPED', 'Dikirim'),
        ('COMPLETED', 'Selesai'),
        ('CANCELLED', 'Dibatalkan'),
    )
    PAYMENT_METHOD_CHOICES = (
        ('BANK_BCA', 'Transfer Bank BCA'),
        ('BANK_BRI', 'Transfer Bank BRI'),
        ('BANK_MANDIRI', 'Transfer Bank Mandiri'),
        ('QRIS', 'QRIS'),
    )
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    reseller = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reseller_orders')
    
    # Financial details
    base_price = models.DecimalField(max_digits=12, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    platform_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Payment
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='BANK_BCA')
    payment_proof = models.ImageField(upload_to='payment_proofs/', null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Shipping details
    shipping_name = models.CharField(max_length=100, blank=True)
    shipping_phone = models.CharField(max_length=20, blank=True)
    shipping_address = models.TextField(blank=True)
    
    def __str__(self):
        return f"Order {self.id} by {self.buyer.username}"

class CommissionLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='commissions')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='commission_logs')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.amount}"

class Withdrawal(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Menunggu Proses'),
        ('APPROVED', 'Disetujui & Ditransfer'),
        ('REJECTED', 'Ditolak'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='withdrawals')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    bank_name = models.CharField(max_length=50)
    account_number = models.CharField(max_length=50)
    account_name = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Withdrawal {self.amount} by {self.user.username}"

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='contact_messages')
    admin_reply = models.TextField(blank=True)
    replied_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Pesan dari {self.name} - {self.subject}"
