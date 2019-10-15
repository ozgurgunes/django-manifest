# -*- coding: utf-8 -*-
""" Manifest URLs
"""

from django.contrib.auth import views as auth_views
from django.urls import re_path
from django.views.generic import TemplateView

from manifest import defaults, views
from manifest.forms import PictureUploadForm, RegionUpdateForm

urlpatterns = [
    # fmt: off
    # Authentication basics
    re_path(
        r"^login/$",
        views.AuthLoginView.as_view(),
        name="auth_login"),

    re_path(
        r"^logout/$",
        views.AuthLogoutView.as_view(),
        name="auth_logout"),

    re_path(
        r"^register/$",
        views.AuthRegisterView.as_view(),
        name="auth_register"),

    re_path(
        r"^register/complete/$",
        TemplateView.as_view(
            template_name="manifest/auth_register_complete.html",
            extra_context={
                "activation_required":
                defaults.MANIFEST_ACTIVATION_REQUIRED,
                "activation_days":
                defaults.MANIFEST_ACTIVATION_DAYS}),
        name="auth_register_complete"),

    re_path(
        r"^activate/(?P<username>\w+)/(?P<token>\w+)/$",
        views.AuthActivateView.as_view(),
        name="auth_activate"),

    # Disabled account
    re_path(
        r"^disabled/$",
        TemplateView.as_view(
            template_name="manifest/auth_disabled.html"),
        name="auth_disabled"),

    # Reset password using django.contrib.auth.views
    re_path(
        r"^password/reset/$",
        auth_views.PasswordResetView.as_view(
            template_name="manifest/password_reset_form.html",
            email_template_name="manifest/emails/password_reset_message.txt"),
        name="password_reset"),

    re_path(
        r"^password/reset/done/$",
        auth_views.PasswordResetDoneView.as_view(
            template_name="manifest/password_reset_done.html"),
        name="password_reset_done"),

    re_path(
        r"^password/reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="manifest/password_reset_confirm.html"),
        name="password_reset_confirm"),

    re_path(
        r"^password/reset/complete/$",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="manifest/password_reset_complete.html"),
        name="password_reset_complete"),

    # Profile views
    re_path(
        r"^profile/$",
        views.AuthProfileView.as_view(),
        name="user_profile"),

    re_path(
        r"^profile/setting/$",
        views.AuthProfileView.as_view(
            template_name="manifest/profile_settings.html"),
        name="profile_settings"),

    re_path(
        r"^profile/update/$",
        views.ProfileUpdateView.as_view(),
        name="profile_update"),

    re_path(
        r"^profile/picture/$",
        views.ProfileUpdateView.as_view(
            form_class=PictureUploadForm,
            template_name="manifest/picture_upload.html"),
        name="picture_upload"),

    re_path(
        r"^profile/region/$",
        views.ProfileUpdateView.as_view(
            form_class=RegionUpdateForm,
            template_name="manifest/region_update.html"),
        name="region_update"),

    # Email change and confirmation
    re_path(
        r"^email/change/$",
        views.EmailChangeView.as_view(),
        name="email_change"),

    re_path(
        r"^email/change/done/$",
        views.AuthProfileView.as_view(
            template_name="manifest/email_change_done.html"),
        name="email_change_done"),

    re_path(
        r"^email/change/(?P<username>\w+)/(?P<token>\w+)/$",
        views.EmailChangeConfirmView.as_view(),
        name="email_change_confirm"),

    re_path(
        r"^email/change/complete/$",
        TemplateView.as_view(
            template_name="manifest/email_change_complete.html"),
        name="email_change_complete"),

    # Password change
    re_path(
        r"^password/change/$",
        views.PasswordChangeView.as_view(),
        name="password_change"),
    re_path(
        r"^password/change/done/$",
        TemplateView.as_view(
            template_name="manifest/password_change_complete.html"),
        name="password_change_done"),

    # User views
    re_path(
        r"^users/$",
        views.UserListView.as_view(),
        name="user_list"),

    re_path(
        r"^users/(?P<username>\w+)/$",
        views.UserDetailView.as_view(),
        name="user_detail"),
    # fmt: on
]
