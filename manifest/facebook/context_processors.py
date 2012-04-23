# -*- coding: utf-8 -*-
from django.conf import settings

def facebook_page_id(request):
    return {'FACEBOOK_PAGE_ID': settings.FACEBOOK_PAGE_ID}

def facebook_app_id(request):
    return {'FACEBOOK_APP_ID': settings.FACEBOOK_APP_ID}

