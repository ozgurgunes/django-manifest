# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from manifest.profiles.forms import ProfileForm, ProfilePictureForm
from manifest.accounts.views import ProfileUpdate

urlpatterns = patterns('',

    url(r'^settings/update/picture/$', 
        ProfileUpdate.as_view(profile_form=ProfilePictureForm), 
        name='profiles_picture_update'),
        
    url(r'^settings/update/profile/$', 
        ProfileUpdate.as_view(profile_form=ProfileForm),
        name='profiles_profile_update'),
                                            
)
