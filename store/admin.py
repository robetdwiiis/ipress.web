from django.contrib import admin
from .models import Product, Order, CommissionLog

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock')

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'buyer', 'product', 'total_price', 'status', 'created_at')
    list_filter = ('status', 'created_at')

class CommissionLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'description', 'created_at')
    
admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(CommissionLog, CommissionLogAdmin)
