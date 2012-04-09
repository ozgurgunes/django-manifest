# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.sites.models import Site

site = Site.objects.get_current()

def site_url(request):
    return {'SITE_URL': 'http://' + site.domain}

def site_name(request):
    return {'SITE_NAME': site.name}

def remote_addr(request):
    return {'REMOTE_ADDR': request.META['REMOTE_ADDR']}
        
def gmap(request):
    return {'GMAPS_API_KEY': settings.GMAPS_API_KEY }