# -*- coding: utf-8 -*-
from manifest.accounts.forms import ProfileForm

class FacebookProfileForm(ProfileForm):
    
    class Meta:
        exclude = ['facebook_id', 'facebook_token', 'facebook_username', 
                        'facebook_expires', 'facebook_link', 'facebook_verified']
        