# -*- coding: utf-8 -*-
"""
Django settings for {{ project_name }} project.

For more information on this file, see
https://docs.djangoproject.com/en/{{ docs_version }}/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/{{ docs_version }}/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
BASE_URL = '/'


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/{{ docs_version }}/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '{{ secret_key }}'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = DEBUG
THUMBNAIL_DEBUG = DEBUG

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    # Django Contrib Apps
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.flatpages',
    'django.contrib.humanize',	    
    'django.contrib.messages',    
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',

    # Django Manifest Apps
    'manifest.core',
    'manifest.accounts',
    'manifest.bootstrap',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    # Enable to use browsers locale settings
    # 'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    # Django Manifest Middlewares
    'manifest.facebook.middleware.FacebookMiddleware',
)

ROOT_URLCONF = '{{ project_name }}.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = '{{ project_name }}.wsgi.application'


# Database
# https://docs.djangoproject.com/en/{{ docs_version }}/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.',    # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '',                         # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': '',                         # Not used with sqlite3.
        'PASSWORD': '',                     # Not used with sqlite3.
        'HOST': '',                         # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                         # Set to empty string for default. Not used with sqlite3.
    }
}


# Internationalization
# https://docs.djangoproject.com/en/{{ docs_version }}/topics/i18n/

TIME_ZONE = 'UTC' #'Europe/Istanbul'
USE_TZ = True

USE_I18N = True
USE_L10N = True

LANGUAGE_CODE = 'en-us' #'tr-tr'

ugettext = lambda s: s
# Languages Django Manifest provide translations for, out of the box.
LANGUAGES = (
  ('en', ugettext('English')),
  ('tr', ugettext('Turkish')),
)

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# Project specific configuration
SITE_ID = 1

# SITE_URL needed if project will not be served at domain root
SITE_URL = BASE_URL


# People who get code error notifications.
# In the format (('Full Name', 'email@example.com'), ('Full Name', 'anotheremail@example.com')
ADMINS = (
	# ('Your Name', 'your_email@example.com'),
)

# Not-necessarily-technical managers of the site. They get broken link
# notifications and other various emails.
MANAGERS = ADMINS

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, 'httpdocs', 'media/')

# URL that handles the media served from MEDIA_ROOT.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = os.path.join(BASE_URL, 'media/')

# Absolute path to the directory static files should be collected to.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = os.path.join(BASE_DIR, 'httpdocs', 'static/')

# URL that handles the static files served from STATIC_ROOT.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = os.path.join(BASE_URL, 'static/')

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.eggs.Loader',
)

# List of locations of the template source files, in search order.
TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, '{{ project_name }}', 'templates/'),
)

# List of processors used by RequestContext to populate the context.
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.core.context_processors.request',
    'django.core.context_processors.csrf',
    'django.contrib.messages.context_processors.messages',
)


# User registration & authentication
AUTHENTICATION_BACKENDS = (
    # Django Manifest
    'manifest.accounts.backends.AuthenticationBackend',
    # Django Contrib
    'django.contrib.auth.backends.ModelBackend',
)

# Django Auth Settings
AUTH_USER_MODEL = 'accounts.User'

# The email backend to use.
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Host for sending email.
EMAIL_HOST = '' 
EMAIL_PORT = 587

# SMTP Authentication
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False

# Automated correspondence
DEFAULT_FROM_EMAIL = 'Django Manifest <django.manifest@localhost>'
EMAIL_SUBJECT_PREFIX = '[Django Manifest] '

# local_settings.py can be used to override environment-specific settings
# like database and email that differ between development and production.
try:
    from local_settings import *
except ImportError:
    pass
    