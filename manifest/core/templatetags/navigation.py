# -*- coding: utf-8 -*-
import re
from django import template
from django.core.urlresolvers import reverse

register = template.Library()

@register.simple_tag
def active_url(request, urls, css=None):
    """
    Highlight menu item based on url tag.
    
    Returns a css class if ``request.path`` is in given ``url``.
    
    :param url:
        Django url to be reversed.

    :param css:
        Css class to be returned for highlighting. Return active if none set.

    """
    if request.path in (reverse(url) for url in urls.split()):
        return css if css else 'active'
    return ''

@register.simple_tag
def active_path(request, pattern, css=None):
    """
    Highlight menu item based on path.
    
    Returns a css class if ``request.path`` is in given ``pattern``.
    
    :param pattern:
        Regex url pattern.

    :param css:
        Css class to be returned for highlighting. Return active if none set.

    """
    if re.search(pattern, request.path):
        return css if css else 'active'
    return ''
