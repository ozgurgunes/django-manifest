# -*- coding: utf-8 -*-
""" Manifest Context Processors
"""

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site

from manifest import defaults


def site(request):
    return {"site": get_current_site(request)}


def installed_apps(request):
    return {"INSTALLED_APPS": getattr(settings, "INSTALLED_APPS", None)}


def messages(request):
    return {"MANIFEST_USE_MESSAGES": defaults.MANIFEST_USE_MESSAGES}


def user_ip(request):
    return {"user_ip": request.META["REMOTE_ADDR"]}
