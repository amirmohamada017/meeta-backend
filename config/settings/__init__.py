import os

DEBUG_ENV = os.getenv('DEBUG', 'True')

if DEBUG_ENV.lower() in ('false', '0', 'no', 'not', 'null', 'none'):
    from .production import *
else:
    from .development import *
