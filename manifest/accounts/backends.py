# -*- coding: utf-8 -*-
from django.contrib.sites.models import Site
from django.core import validators
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

from manifest.accounts import defaults


class AuthenticationBackend(ModelBackend):
    """
    Custom backend because the user must be able to supply a ``email`` or
    ``username`` to the login form.

    """
    def authenticate(self, identification, password=None, 
                        check_password=True):
        """
        Authenticates a user through the combination email/username with
        password.

        :param identification:
            A string containing the username or email of the user that is
            trying to authenticate.

        :password:
            Optional string containing the password for the user.

        :param check_password:
            Boolean that defines if the password should be checked for this
            user.  Always keep this ``True``. This is only used by accounts at
            activation when a user opens a page with a secret hash.

        :return: The logged in :class:`User`.

        """
        try:
            validators.validate_email(identification)
            try: 
                user = get_user_model().objects.get(email__iexact=identification)
            except get_user_model().DoesNotExist: 
                return None
        except:
            validators.ValidationError
            try: 
                user = get_user_model().objects.get(username__iexact=identification)
            except get_user_model().DoesNotExist: 
                return None
        if check_password:
            if user.check_password(password):
                return user
            return None
        else: 
            return user

    def get_user(self, user_id):
        try: 
            return get_user_model().objects.get(pk=user_id)
        except get_user_model().DoesNotExist:
            return None
