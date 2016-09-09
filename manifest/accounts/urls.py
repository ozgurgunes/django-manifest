# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required

from manifest.accounts import views as accounts_views
from manifest.accounts import defaults


urlpatterns = patterns('',
    # Signup, login and logout
    url(r'^login/$', 
        accounts_views.Login.as_view(),
        name='accounts_login'),

    url(r'^logout/$', 
        auth_views.logout, {
            'next_page': defaults.ACCOUNTS_REDIRECT_ON_LOGOUT,
            'template_name': 'accounts/logout.html'},
        name='accounts_logout'), 

    url(r'^register/$', 
        accounts_views.Register.as_view(),      
        name='accounts_register'),

    url(r'^register/complete/(?P<username>\w+)/$', 
        accounts_views.UserView.as_view(
            template_name='accounts/register_complete.html',
            extra_context={
                'accounts_activation_required': 
                    defaults.ACCOUNTS_ACTIVATION_REQUIRED,
                'accounts_activation_days': 
                    defaults.ACCOUNTS_ACTIVATION_DAYS}),
        name='accounts_register_complete'),

    # Activate
    url(r'^activate/(?P<username>\w+)/(?P<activation_key>\w+)/$', 
        accounts_views.Activate.as_view(), 
        name='accounts_activate'),

    # Disabled
    url(r'^disabled/(?P<username>\w+)/$', 
        accounts_views.UserView.as_view(
            template_name='accounts/disabled.html'), 
        name='accounts_disabled'),

    # Settings
    url(r'settings/$', 
        accounts_views.UserTemplateView.as_view(),
        name='accounts_settings'),

    # Edit profile
    url(r'^settings/update/$', 
        accounts_views.ProfileUpdate.as_view(),    
        name='accounts_update'),

    # Reset password using django.contrib.auth.views
    url(r'^password/reset/$', 
        auth_views.password_reset, dict(
            template_name='accounts/password_reset_form.html',
            email_template_name='accounts/emails/password_reset_message.txt'),
        name='accounts_password_reset'),

    url(r'^password/reset/done/$', 
        auth_views.password_reset_done, dict(
            template_name='accounts/password_reset_done.html'),
        name='password_reset_done'),

    url(r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$', 
        auth_views.password_reset_confirm, dict(
            template_name='accounts/password_reset_confirm.html'),
        name='password_reset_confirm'),

    url(r'^password/reset/complete/$', 
        auth_views.password_reset_complete, dict(
            template_name='accounts/password_reset_complete.html'),
        name='password_reset_complete'),

    # Change email and confirm it
    url(r'^email/change/$', 
        accounts_views.EmailChange.as_view(),
        name='accounts_email_change'),

    url(r'^email/change/done/(?P<username>\w+)/$', 
        accounts_views.UserView.as_view(
            template_name='accounts/email_change_done.html'),
        name='accounts_email_change_done'),
    
    url(r'^email/change/confirm/(?P<username>\w+)/(?P<confirmation_key>\w+)/$', 
        accounts_views.EmailConfirm.as_view(),
        name='accounts_email_confirm'),

    url(r'^email/change/complete/(?P<username>\w+)/$', 
        accounts_views.UserView.as_view(
            template_name='accounts/email_change_complete.html'),
        name='accounts_email_change_complete'),

    # Change password
    url(r'^password/change/$', 
        accounts_views.PasswordChange.as_view(),
        name='accounts_password_change'),

    url(r'^password/change/done/(?P<username>\w+)/$', 
        accounts_views.UserView.as_view(
            template_name='accounts/password_change_complete.html'),
        name='accounts_password_change_done'),

    # View profiles
    url(r'^profiles/(?P<username>(?!logout|register|login|password|account|profile)\w+)/$', 
        accounts_views.ProfileDetail.as_view(),
        name='accounts_profile_detail'),

    url(r'^profiles/$', 
        accounts_views.ProfileList.as_view(),
        name='accounts_profile_list'),
)
