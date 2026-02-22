import os
from dotenv import load_dotenv
from django.core.wsgi import get_wsgi_application

load_dotenv()
setup = os.getenv('DJANGO_ENV', 'dev')
if not setup:
    raise EnvironmentError("DJANGO_ENV not set. Ensure the environment variable is configured correctly.")

os.environ.setdefault('DJANGO_SETTINGS_MODULE', f'config.settings.{setup}')

application = get_wsgi_application()
