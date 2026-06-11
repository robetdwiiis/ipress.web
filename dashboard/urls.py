from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='home'),
    
    # Products
    path('products/', views.product_list, name='products'),
    path('products/add/', views.product_create, name='product_add'),
    path('products/<int:pk>/edit/', views.product_update, name='product_edit'),
    path('products/<int:pk>/delete/', views.product_delete, name='product_delete'),
    
    # Orders
    path('orders/', views.order_list, name='orders'),
    path('orders/<int:pk>/status/', views.order_status_update, name='order_status_update'),
    path('orders/<int:pk>/delete/', views.order_delete, name='order_delete'),
    
    # Resellers
    path('resellers/', views.reseller_list, name='resellers'),
    path('resellers/add/', views.reseller_create, name='reseller_add'),
    path('resellers/applications/', views.reseller_applications, name='reseller_applications'),
    path('resellers/applications/<int:pk>/approve/', views.reseller_approve, name='reseller_approve'),
    path('resellers/applications/<int:pk>/reject/', views.reseller_reject, name='reseller_reject'),

    # Withdrawals
    path('withdrawals/request/', views.reseller_withdraw, name='reseller_withdraw'),
    path('withdrawals/', views.owner_withdrawals, name='owner_withdrawals'),
    path('withdrawals/<int:pk>/approve/', views.owner_withdrawal_approve, name='owner_withdrawal_approve'),
    path('withdrawals/<int:pk>/reject/', views.owner_withdrawal_reject, name='owner_withdrawal_reject'),

    # Withdrawals
    path('withdrawals/request/', views.reseller_withdraw, name='reseller_withdraw'),
    path('withdrawals/', views.owner_withdrawals, name='owner_withdrawals'),
    path('withdrawals/<int:pk>/approve/', views.owner_withdrawal_approve, name='owner_withdrawal_approve'),
    path('withdrawals/<int:pk>/reject/', views.owner_withdrawal_reject, name='owner_withdrawal_reject'),

    # Inbox
    path('inbox/', views.owner_inbox, name='owner_inbox'),
    path('inbox/<int:pk>/read/', views.owner_inbox_read, name='owner_inbox_read'),
    path('inbox/<int:pk>/reply/', views.owner_inbox_reply, name='owner_inbox_reply'),
]
