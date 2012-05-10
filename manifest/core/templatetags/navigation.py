# -*- coding: utf-8 -*-
import re
from django import template
from django.core.urlresolvers import reverse

register = template.Library()

@register.simple_tag
def active_url(request, urls):
    if request.path in (reverse(url) for url in urls.split()):
        return 'active'
    return ''

@register.simple_tag
def active_path(request, pattern):
    if re.search(pattern, request.path):
        return 'active' 
    return ''

@register.simple_tag
def current_url(request, urls):
    if request.path in (reverse(url) for url in urls.split()):
        return 'current'
    return ''

@register.simple_tag
def current_path(request, pattern):
    if re.search(pattern, request.path):
        return 'current' 
    return ''
