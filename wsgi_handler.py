import sys, os
DIRNAME = os.path.abspath(os.path.dirname(__file__).decode('utf-8'))
sys.path = [DIRNAME+"/..",DIRNAME] + sys.path

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
       
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

