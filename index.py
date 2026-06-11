import os
import sys

path = os.path.dirname(os.path.abspath(__file__))
if path not in sys.path:
    sys.path.append(path)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
django.setup()

# Auto-migrate database saat startup
from django.core.management import call_command
try:
    call_command('migrate', '--noinput')
except Exception as e:
    print(f"Migration warning: {e}")

from django.core.wsgi import get_wsgi_application
app = get_wsgi_application()
