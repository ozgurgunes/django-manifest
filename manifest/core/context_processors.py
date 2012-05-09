# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.sites.models import Site

def site(request):
    site = Site.objects.get_current()
    return {
        'SITE_NAME': getattr(settings, 'SITE_NAME', site.name),
        'SITE_DOMAIN': getattr(settings, 'SITE_DOMAIN', site.domain),
        'SITE_PATH': getattr(settings, 'SITE_PATH', ''),
        'SITE_URL': getattr(settings, 'SITE_URL', ''),
    }

def site_name(request):
    return {'SITE_NAME': Site.objects.get_current().name}

def site_domain(request):
    return {'SITE_DOMAIN': Site.objects.get_current().domain}

def site_path(request):
    return {'SITE_PATH': getattr(settings, 'SITE_PATH', None)}

def site_url(request):
    return {'SITE_URL': getattr(settings, 'SITE_URL', None)}

def installed_apps(request):
    return {'INSTALLED_APPS': getattr(settings, 'INSTALLED_APPS', None)}

def remote_addr(request):
    return {'REMOTE_ADDR': request.META['REMOTE_ADDR']}

