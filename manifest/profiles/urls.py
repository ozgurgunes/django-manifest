# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from manifest.profiles.forms import ProfileForm, ProfilePictureForm
from manifest.accounts.views import profile_edit
from relationships import views as relationship_views

urlpatterns = patterns('',

    url(r'^edit/picture/$', profile_edit, dict(form=ProfilePictureForm), 
                                        name='profiles_picture_edit'),
    url(r'^edit/$', profile_edit, dict(form=ProfileForm), 
                                        name='profiles_picture_edit'),
                                            
)
