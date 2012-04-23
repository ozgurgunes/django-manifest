# -*- coding: utf-8 -*-
from django import template
from django.contrib.auth.models import User

register = template.Library()

class Avatar(template.Node):
    
    def __init__(self, user, type=None):
        self.user = template.Variable(user)
        self.type = type

    def render(self, context):
        uid = User.objects.select_related().get(username=self.user.resolve(context)).social_auth.get(provider='facebook').uid
        if self.type:
            return 'https://graph.facebook.com/%s/picture?type=%s' % (uid, self.type)
        return 'https://graph.facebook.com/%s/picture' % uid
        

@register.tag
def facebook_avatar(parser, token):
    bits = token.contents.split()
    if len(bits) < 2:
        raise template.TemplateSyntaxError, "facebook_avatar tag takes at least one argument (user)"
    return Avatar(bits[1], bits[2]) if len(bits) == 3 else Avatar(bits[1])
