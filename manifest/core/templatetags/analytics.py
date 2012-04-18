from django import template
from django.conf import settings

register = template.Library()

@register.inclusion_tag("core/analytics.html")
def analytics(account=None, *args, **kwargs):
    if not account:
        try:
            account = settings.GOOGLE_ANALYTICS_ACCOUNT
        except:
            raise template.TemplateSyntaxError, "Analytics account could not found either in tag parameters or settings"    
    return {'account': account, 'params':kwargs }
