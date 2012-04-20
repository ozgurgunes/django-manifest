# -*- coding: utf-8 -*-
from django.conf import settings
from django.conf.urls import patterns, include, url
from django.views.generic.simple import direct_to_template

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'mysite.views.home', name='home'),
    # url(r'^mysite/', include('mysite.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    url(r'^$', direct_to_template, {'template': 'homepage.html',}, name='home'),
    url(r'^announces/', include('announcements.urls')),
    url(r'^relations/', include('relationships.urls')),
    url(r'^accounts/', include('social_auth.urls')),
    url(r'^accounts/', include('manifest.accounts.urls')),
    url(r'^profiles/', include('manifest.profiles.urls')),

    url(r'^(?P<username>\w+)/$', 'manifest.profiles.views.profile_detail', name='profiles_profile_detail'),
    url(r'^(?P<username>\w+)/comments/$', 'manifest.profiles.views.comment_list', name='profiles_comments_list'),
    url(r'^(?P<username>\w+)/friends/$', 'manifest.profiles.views.friend_list', name='profiles_friends_list'),

)
