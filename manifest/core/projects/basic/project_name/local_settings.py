# -*- coding: utf-8 -*-
"""
Django local settings for {{ project_name }} project.
"""

import os
import settings

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
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
