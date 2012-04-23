# -*- coding: utf-8 -*-
from django.conf import settings

# SOCIAL_AUTH_PIPELINE = settings.SOCIAL_AUTH_PIPELINE + getattr(settings, 'MANIFEST_FACEBOOK_PIPELINE', (
#     'manifest.facebook.pipeline.get_info',
#     )
    
MANIFEST_FACEBOOK_FRIENDS = getattr(settings, 'MANIFEST_FACEBOOK_FRIENDS', True)
MANIFEST_FACEBOOK_LIKES = getattr(settings, 'MANIFEST_FACEBOOK_LIKES', False)
MANIFEST_FACEBOOK_SYNC = getattr(settings, 'MANIFEST_FACEBOOK_SYNC', ['friends', 'likes'])
