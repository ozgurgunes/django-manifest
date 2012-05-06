# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required

from manifest.accounts import views as accounts_views
from manifest.accounts import settings as accounts_settings

urlpatterns = patterns('',
    # Signup, login and logout
    url(r'^login/$', accounts_views.login, name='accounts_login'),
    url(r'^logout/$', auth_views.logout, {
                            'next_page': accounts_settings.ACCOUNTS_REDIRECT_ON_SIGNOUT,
                            'template_name': 'accounts/logout.html'},
                                    name='accounts_logout'),                                    
    url(r'^register/$', accounts_views.register, name='accounts_register'),
    url(r'^register/complete/(?P<username>\w+)/$', accounts_views.UserTemplate.as_view(
                                        template_name='accounts/register_complete.html',
                                        extra_context={
                                                'accounts_activation_required': accounts_settings.ACCOUNTS_ACTIVATION_REQUIRED,
                                                'accounts_activation_days': accounts_settings.ACCOUNTS_ACTIVATION_DAYS
                                                }
                                        ),
                                    name='accounts_register_complete'),

    # Activate
    url(r'^activate/(?P<username>\w+)/(?P<activation_key>\w+)/$', accounts_views.activate,
                                    name='accounts_activate'),

    # Disabled
    url(r'^disabled/(?P<username>\w+)/$', accounts_views.UserTemplate.as_view(template_name='accounts/disabled.html'), 
                                    name='accounts_disabled'),

    # Settings
    url(r'settings/$', accounts_views.settings, dict(template_name='accounts/settings.html'), 
                                    name='accounts_settings'),

    # Reset password
    url(r'^password/reset/$', auth_views.password_reset, {
                            'template_name': 'accounts/password_reset_form.html',
                            'email_template_name': 'accounts/emails/password_reset_message.txt'},
                                    name='accounts_password_reset'),
    url(r'^password/reset/done/$', auth_views.password_reset_done, {
                            'template_name': 'accounts/password_reset_done.html'},
                                    name='accounts_password_reset_complete'),
    url(r'^password/reset/confirm/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', auth_views.password_reset_confirm, {
                            'template_name': 'accounts/password_reset_confirm.html'},
                                    name='accounts_password_reset_confirm'),
    url(r'^password/reset/complete/$', auth_views.password_reset_complete, {
                            'template_name': 'accounts/password_reset_complete.html'},
                                    name='accounts_password_reset_complete'),

    # Change email and confirm it
    url(r'^email/change/$', accounts_views.email_change, {
                            'template_name': 'accounts/email_change_form.html'},
                                    name='accounts_email_change'),
    url(r'^email/change/done/(?P<username>\w+)/$', accounts_views.UserTemplate.as_view(
                                        template_name='accounts/email_change_done.html'),
                                    name='accounts_email_change_done'),
    url(r'^email/change/confirm/(?P<confirmation_key>\w+)/$', accounts_views.email_confirm,
                                    name='accounts_email_confirm'),
    url(r'^email/change/complete/(?P<username>\w+)/$', accounts_views.UserTemplate.as_view(
                                        template_name='accounts/email_change_complete.html'),
                                    name='accounts_email_change_complete'),
    # Change password
    url(r'^password/change/$', accounts_views.password_change,
                                    name='accounts_password_change'),
    url(r'^password/change/done/(?P<username>\w+)/$', accounts_views.UserTemplate.as_view(
                                        template_name='accounts/password_change_complete.html'),
                                    name='accounts_password_change_done'),

    # Edit profile
    url(r'^edit/$', accounts_views.profile_edit,
                                    name='accounts_profile_edit'),

    # View profiles
    url(r'^(?P<username>(?!logout|register|login|password|account|profile)\w+)/$', accounts_views.ProfileDetail.as_view(),
                                    name='accounts_profile_detail'),
    url(r'^profiles/$', accounts_views.ProfileList.as_view(),
                                    name='accounts_profile_list'),
)
