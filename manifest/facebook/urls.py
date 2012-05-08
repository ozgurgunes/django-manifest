# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from manifest.facebook.views import iframe

urlpatterns = patterns('',

    url(r'^connect/$', TemplateView.as_view(template_name='facebook/connect.html'), name='facebook_connect'),
    url(r'^iframe/$', iframe, name='facebook_iframe'),
    
)
