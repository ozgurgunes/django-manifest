# -*- coding: utf-8 -*-
from django.conf import settings

def facebook_app_id(request):
    return {'FACEBOOK_APP_ID': getattr(settings, 'FACEBOOK_APP_ID', '')}

def facebook_page_id(request):
    return {'FACEBOOK_PAGE_ID': getattr(settings, 'FACEBOOK_PAGE_ID', '')}

def facebook_page_slug(request):
    return {'FACEBOOK_PAGE_SLUG': getattr(settings, 'FACEBOOK_PAGE_SLUG', '')}

