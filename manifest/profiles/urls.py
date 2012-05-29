# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from manifest.profiles.forms import ProfileForm, ProfilePictureForm
from manifest.accounts.views import profile_edit
from relationships import views as relationship_views

urlpatterns = patterns('',

    url(r'^settings/update/picture/$', profile_edit, dict(form=ProfilePictureForm), 
                                        name='profiles_picture_update'),
    url(r'^settings/update/profile/$', profile_edit, dict(form=ProfileForm), 
                                        name='profiles_profile_update'),
                                            
)
