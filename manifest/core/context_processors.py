# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.sites.models import Site


def site_url(request):
    return {'SITE_URL': getattr(settings, 'SITE_URL', None)}

def site_domain(request):
    return {'SITE_DOMAIN': Site.objects.get_current().domain}

def site_name(request):
    return {'SITE_NAME': Site.objects.get_current().name}

def installed_apps(request):
    return {'INSTALLED_APPS': getattr(settings, 'INSTALLED_APPS', None)}

def remote_addr(request):
    return {'REMOTE_ADDR': request.META['REMOTE_ADDR']}

