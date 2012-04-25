# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('',

    url(r'^connect/$', direct_to_template, {'template': 'facebook/connect.html'}, name='facebook_connect'),
    
)
