# -*- coding: utf-8 -*-
from django.conf import settings

MANIFEST_FACEBOOK_FRIENDS = getattr(settings, 
                                'MANIFEST_FACEBOOK_FRIENDS', False)
MANIFEST_FACEBOOK_LIKES = getattr(settings, 
                                'MANIFEST_FACEBOOK_LIKES', False)
MANIFEST_FACEBOOK_SYNC = getattr(settings, 
                                'MANIFEST_FACEBOOK_SYNC', 
                                ['friends', 'likes'])
