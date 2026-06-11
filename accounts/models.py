from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('OWNER', 'Owner'),
        ('RESELLER', 'Reseller'),
        ('BUYER', 'Buyer'),
    )
    RESELLER_STATUS_CHOICES = (
        ('NONE', 'None'),
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='BUYER')
    reseller_status = models.CharField(max_length=20, choices=RESELLER_STATUS_CHOICES, default='NONE')
    upline = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='downlines')
    wallet_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    # Profile fields for Buyer
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=10, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    
    # Payment Info
    bank_name = models.CharField(max_length=100, blank=True)
    account_number = models.CharField(max_length=50, blank=True)

    
    def is_owner(self):
        return self.role == 'OWNER' or self.is_superuser
        
    def is_reseller(self):
        return self.role == 'RESELLER'
    
    def get_display_name(self):
        if self.first_name:
            return f"{self.first_name} {self.last_name}".strip()
        return self.username
        
    def __str__(self):
        return f"{self.get_display_name()} ({self.get_role_display()})"

class ResellerApplication(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reseller_applications')
    social_media_link = models.URLField(max_length=200, blank=True, help_text="Link Instagram, TikTok, atau toko online Anda")
    marketing_plan = models.TextField(help_text="Bagaimana Anda berencana memasarkan produk kami?")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Pengajuan {self.user.username} - {self.status}"
