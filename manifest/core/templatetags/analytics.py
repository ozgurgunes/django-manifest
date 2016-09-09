# -*- coding: utf-8 -*-
from django import template
from django.conf import settings

register = template.Library()

@register.inclusion_tag("core/analytics.html")
def analytics(account=None, *args, **kwargs):
    """
    Simple Google Analytics integration.

    First looks for an ``account`` parameter. If not supplied, uses
    Django ``GOOGLE_ANALYTICS_ACCOUNT`` setting. If account not set, 
    raises ``TemplateSyntaxError``.

    :param account:
        Google Analytics account id to be used.

    """
    if not account:
        try:
            account = settings.GOOGLE_ANALYTICS_ACCOUNT
        except:
            raise template.TemplateSyntaxError( 
                    "Analytics account could not found either "
                    "in tag parameters or settings")
    return {'account': account, 'params':kwargs }
