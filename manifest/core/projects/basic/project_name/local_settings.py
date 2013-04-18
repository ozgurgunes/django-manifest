# -*- coding: utf-8 -*-
"""
Django local settings for {{ project_name }} project.
"""

import os
import settings

PATH = os.path.dirname(os.path.dirname(__file__))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',     # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': os.path.join(PATH, 'db.sqlite3'),   # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': '',
        'PASSWORD': '',
        'HOST': '',     # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',     # Set to empty string for default.
    }
}

MIDDLEWARE_CLASSES = settings.MIDDLEWARE_CLASSES + (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

INSTALLED_APPS = settings.INSTALLED_APPS + (
    'debug_toolbar',
)

# Settings for Django Debug Toolbar
INTERNAL_IPS = ('127.0.0.1',)
DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
#    'SHOW_TOOLBAR_CALLBACK': custom_show_toolbar,
#    'EXTRA_SIGNALS': ['{{ project_name }}.signals.MySignal'],
#    'HIDE_DJANGO_SQL': False,
#    'TAG': 'div',
#    'ENABLE_STACKTRACES' : True,
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
