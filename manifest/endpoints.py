# -*- coding: utf-8 -*-
""" Manifest REST API URLs
"""

from django.conf.urls import url

from manifest import api_views
from manifest.messages import REGION_UPDATE_SUCCESS
from manifest.serializers import ProfileUpdateSerializer, RegionUpdateSerializer

urlpatterns = [
    # fmt: off
    # Authentication basics
    url(
        r'^login/$',
        api_views.AuthLoginAPIView.as_view(),
        name='auth_login_api'),

    url(r'^logout/$',
        api_views.AuthLogoutAPIView.as_view(),
        name='auth_logout_api'),

    url(r'^register/$',
        api_views.AuthRegisterAPIView.as_view(),
        name='auth_register_api'),

    url(r'^activate/$',
        api_views.AuthActivateAPIView.as_view(),
        name='auth_activate_api'),

    # Reset password
    url(r'^password/reset/$',
        api_views.PasswordResetAPIView.as_view(),
        name='password_reset_api'),

    url(r'^password/reset/verify/$',
        api_views.PasswordResetVerifyAPIView.as_view(),
        name='password_reset_verify_api'),

    url(r'^password/reset/confirm/$',
        api_views.PasswordResetConfirmAPIView.as_view(),
        name='password_reset_confirm_api'),

    # Profile views
    url(r'^profile/$',
        api_views.AuthProfileAPIView.as_view(),
        name='auth_profile_api'),

    url(r'^profile/options/$',
        api_views.ProfileOptionsAPIView.as_view(
            serializer_class=ProfileUpdateSerializer
        ),
        name='profile_options_api'),

    url(r'^profile/update/$',
        api_views.AuthProfileAPIView.as_view(
            serializer_class=ProfileUpdateSerializer
        ),
        name='profile_update_api'),

    url(r'^profile/update/region/$',
        api_views.AuthProfileAPIView.as_view(
            serializer_class=RegionUpdateSerializer,
            success_message=REGION_UPDATE_SUCCESS
        ),
        name='region_update_api'),

    url(r'^picture/upload/$',
        api_views.PictureUploadAPIView.as_view(),
        name='picture_upload_api'),

    # Email change and confirmation
    url(r'^email/change/$',
        api_views.EmailChangeAPIView.as_view(),
        name='email_change_api'),

    url(r'^email/change/confirm/$',
        api_views.EmailChangeConfirmAPIView.as_view(),
        name='email_change_confirm_api'),

    # Password change
    url(r'^password/change/$',
        api_views.PasswordChangeAPIView.as_view(),
        name='password_change_api'),

    # User views
    url(r'^users/$',
        api_views.UserListAPIView.as_view(),
        name='user_list_api'),

    url(r'^users/(?P<username>\w+)/$',
        api_views.UserDetailAPIView.as_view(),
        name='user_detail_api'),
    # fmt: on
]
