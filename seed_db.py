import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.models import User
from store.models import Product

def seed():
    print("Starting database seeding...")
    # Create Owner
    if not User.objects.filter(username='owner').exists():
        owner = User.objects.create_superuser('owner', 'owner@example.com', 'password123')
        owner.role = 'OWNER'
        owner.save()
        print("Created owner user.")
    else:
        print("Owner user already exists.")

    # Create Reseller
    if not User.objects.filter(username='reseller1').exists():
        reseller = User.objects.create_user('reseller1', 'reseller1@example.com', 'password123')
        reseller.role = 'RESELLER'
        reseller.save()
        print("Created reseller user.")
    else:
        print("Reseller user already exists.")

    # Create dummy products
    products = [
        {'name': 'iPhone 15 Pro Max', 'price': 22999000, 'stock': 10, 'desc': 'Titanium, A17 Pro chip, Action button, 48MP Main camera.'},
        {'name': 'iPhone 15', 'price': 15499000, 'stock': 25, 'desc': 'Dynamic Island, 48MP Main camera, USB-C.'},
        {'name': 'iPhone 14', 'price': 11999000, 'stock': 5, 'desc': 'Super Retina XDR display, A15 Bionic chip.'},
    ]

    for p in products:
        if not Product.objects.filter(name=p['name']).exists():
            Product.objects.create(
                name=p['name'],
                price=p['price'],
                stock=p['stock'],
                description=p['desc'],
            )
            print(f"Created product {p['name']}.")
        else:
            print(f"Product {p['name']} already exists.")
    
    print("Seeding completed successfully.")

if __name__ == '__main__':
    seed()
