# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

urlpatterns = patterns('',

    url(r'^connect/$', TemplateView.as_view(template_name='facebook/connect.html'), name='facebook_connect'),
    
)
