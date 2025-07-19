# core/settings/__init__.py
import os

# Default to development settings if not specified
ENV = os.getenv("DJANGO_ENV", "dev")

if ENV == "prod":
    from .prod import *
else:
    from .dev import *
