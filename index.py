import os
import sys

# Tambahkan path root ke sys.path agar Django bisa menemukan modul 'config'
path = os.path.dirname(os.path.abspath(__file__))
if path not in sys.path:
    sys.path.append(path)

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
app = get_wsgi_application()
