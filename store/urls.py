from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('checkout/<int:pk>/', views.checkout_view, name='checkout'),
    path('order/<int:pk>/', views.order_detail, name='order_detail'),
    path('order/<int:pk>/cancel/', views.cancel_order, name='cancel_order'),
    path('order/<int:pk>/upload-proof/', views.upload_payment_proof, name='upload_payment_proof'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('reseller-program/', views.reseller_program, name='reseller_program'),
    path('reseller-program/apply/', views.apply_reseller_view, name='apply_reseller'),
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
]
