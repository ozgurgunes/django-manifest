# -*- coding: utf-8 -*-
""" Manifest Test Settings
"""
# pylint: disable=invalid-name

from django.shortcuts import render
from django.urls import include, path, re_path
from django.views.generic import TemplateView

from rest_framework_jwt.views import (
    obtain_jwt_token,
    refresh_jwt_token,
    verify_jwt_token,
)

from manifest import views
from manifest.forms import RegisterFormToS

TEST_SUCCESS_URL = "/test/"
TEST_REGISTER_FORM_CLASS = RegisterFormToS


def handler404(request, exception=Exception("Page not found!")):
    return render(request, "404.html", status=404)


def handler500(request):
    return render(request, "500.html", status=500)


urlpatterns = [
    # fmt: off
    path("accounts/", include("manifest.urls")),
    path("manifest/", include("manifest.endpoints")),
    path("flatpages/", include("django.contrib.flatpages.urls")),
    path("jwt/obtain/", obtain_jwt_token),
    path("jwt/refresh/", refresh_jwt_token),
    path("jwt/verify/", verify_jwt_token),

    re_path(
        r"^users/(?P<page>\d+)$",
        views.UserListView.as_view(paginate_by=1),
        name="user_list_paginated"),


    re_path(
        r'^test-auth-login-success-url/$',
        views.AuthLoginView.as_view(success_url=TEST_SUCCESS_URL),
        name='test_auth_login_success_url',
    ),
    re_path(
        r'^test-auth-register-success-url/$',
        views.AuthRegisterView.as_view(success_url=TEST_SUCCESS_URL),
        name='test_auth_register_success_url',
    ),
    re_path(
        r'^test-auth-register-form-class/$',
        views.AuthRegisterView.as_view(form_class=TEST_REGISTER_FORM_CLASS),
        name='test_auth_register_form_class',
    ),
    re_path(
        r'^test-auth-activate-success-url/(?P<username>\w+)/(?P<token>\w+)/$',
        views.AuthActivateView.as_view(success_url=TEST_SUCCESS_URL),
        name='test_auth_activate_success_url',
    ),
    re_path(
        r'^test-profile-update-success-url/$',
        views.ProfileUpdateView.as_view(success_url=TEST_SUCCESS_URL),
        name='test_profile_update_success_url',
    ),
    re_path(
        r'^test-email-change-success-url/$',
        views.EmailChangeView.as_view(success_url=TEST_SUCCESS_URL),
        name='test_email_change_success_url',
    ),
    re_path(
        r'^test-email-change-confirm-success-url/'
        r'(?P<username>\w+)/(?P<token>\w+)/$',
        views.EmailChangeConfirmView.as_view(success_url=TEST_SUCCESS_URL),
        name='test_email_change_confirm_success_url',
    ),
    re_path(
        r'^test-password-change-success-url/$',
        views.PasswordChangeView.as_view(success_url=TEST_SUCCESS_URL),
        name='test_password_change_success_url',
    ),

    re_path(
        r'^test-send-mail-mixin-subject/$',
        views.EmailChangeView.as_view(
            email_subject_template_name_new=None
        ),
        name='test_send_mail_mixin_subject',
    ),

    re_path(
        r'^test-send-mail-mixin-message/$',
        views.EmailChangeView.as_view(
            email_message_template_name_new=None
        ),
        name='test_send_mail_mixin_message',
    ),

    re_path(
        r'^test-send-mail-mixin-html/$',
        views.EmailChangeView.as_view(
            email_html_template_name_new=""
            'manifest/emails/confirmation_email_message_new.txt'
        ),
        name='test_send_mail_mixin_html',
    ),

    re_path(
        r'^404$',
        handler404,
        name='page_not_found',
    ),

    re_path(
        r'^500$',
        handler500,
        name='server_error',
    ),

    re_path(
        "^$",
        TemplateView.as_view(template_name="homepage.html"), name="homepage"),

    re_path(
        "^(?!media|static|flatpages)",
        TemplateView.as_view(template_name="vue.html"),
        name="vue",
    ),
    # fmt: on
]
