# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.conf import settings

from django.views.generic import TemplateView


# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', '{{ project_name }}.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    
    # Django Manifest standard homepage:
    url(r'^$', TemplateView.as_view(template_name='homepage.html'), name='home'),

    url(r'^', include('social_auth.urls')),
    url(r'^', include('manifest.facebook.urls')),
    url(r'^', include('manifest.accounts.urls')),
    url(r'^', include('manifest.profiles.urls')),

)
