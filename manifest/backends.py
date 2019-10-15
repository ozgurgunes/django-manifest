# -*- coding: utf-8 -*-
""" Manifest Backends
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.core import validators


class AuthenticationBackend(ModelBackend):
    """
    Custom backend to allow user login with entering
    either an ``email`` or ``username``.

    """

    # pylint: disable=arguments-differ,bad-continuation
    def authenticate(
        self, request, identification, password=None, check_password=True
    ):
        """
        Authenticates user by either email or username with password.

        :param identification:
            String containing email or username.

        :password:
            Optional string containing the password for the user.

        :param check_password:
            Boolean, default is ``True``. User will be authenticated
            without password if ``False``. This is only used for authenticate
            the user when visiting specific pages with a secret token.

        :return: The logged in :class:`User`.

        """
        user_model = get_user_model()
        try:
            validators.validate_email(identification)
            try:
                user = user_model.objects.get(email__iexact=identification)
            except user_model.DoesNotExist:
                return None
        except validators.ValidationError:
            try:
                user = user_model.objects.get(username__iexact=identification)
            except user_model.DoesNotExist:
                return None
        if check_password and user.check_password(password):
            return user
        return None

    def get_user(self, user_id):
        try:
            return get_user_model().objects.get(pk=user_id)
        except get_user_model().DoesNotExist:
            return None
