import os
import sys

path = os.path.dirname(os.path.abspath(__file__))
if path not in sys.path:
    sys.path.append(path)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
django.setup()

from django.core.management import call_command
try:
    call_command('migrate', '--noinput')
except Exception as e:
    print(f"Migration warning: {e}")

# Buat superuser otomatis jika belum ada
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='Admin1234!'
    )
    print("Superuser created!")

from django.core.wsgi import get_wsgi_application
app = get_wsgi_application()
