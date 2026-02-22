import os
from config.settings.base import *

# Tentukan environment berdasarkan ENV variable
ENV = os.environ.get('DJANGO_ENV', 'dev')

if ENV == 'production':
    from .prod import *
elif ENV == 'staging':
    from .staging import *
else:
    from .dev import *
