# -*- coding: utf-8 -*-
""" Manifest Model Managers
"""

import re

from django.contrib.auth.models import (
    AnonymousUser,
    UserManager as BaseManager,
)

from manifest import defaults, signals
from manifest.utils import generate_sha1

SHA1_RE = re.compile("^[a-f0-9]{40}$")


class AccountActivationManager(BaseManager):
    """
    Registration and account activation functionalities for Manifest User model.

    """

    # pylint: disable=arguments-differ,bad-continuation
    def create_user(self, username, email, password, active=False):
        """
        A simple wrapper that creates a new :class:`User`.

        :param username:
            String containing the username of the new user.

        :param email:
            String containing the email address of the new user.

        :param password:
+            String containing the password for the new user.

        :param active:
            Boolean that defines if the user requires activation by clicking
            on a link in an email. Defauts to ``True``.

        :return: :class:`User` instance representing the new user.

        """

        user = super().create_user(username, email, password)

        if isinstance(user.username, str):
            username = user.username.encode("utf-8")
        activation_key = generate_sha1(username)
        user.is_active = active
        user.activation_key = activation_key[1]
        user.save(using=self._db)

        return user

    def activate_user(self, username, activation_key):
        """
        Activate a :class:`User` by supplying a valid ``activation_key``.

        If the key is valid and a user is found, activates the user and
        return it. Also sends the ``ACTIVATION_COMPLETE`` signal.

        :param username:
            String containing the unique username for activation.

        :param activation_key:
            String containing the secret SHA1 for a valid activation.

        :return:
            The newly activated :class:`User` or ``False`` if not successful.

        """
        if SHA1_RE.search(activation_key):
            try:
                user = self.get(
                    username=username, activation_key=activation_key
                )
            except self.model.DoesNotExist:
                return False
            if not user.activation_key_expired():
                user.activation_key = defaults.MANIFEST_ACTIVATED_LABEL
                user.is_active = True
                user.save(using=self._db)
                # Send the ACTIVATION_COMPLETE signal
                signals.ACTIVATION_COMPLETE.send(sender=None, user=user)
                return user
        return False

    def delete_expired_users(self):
        """
        Checks for expired users and delete's the ``User`` associated with
        it. Skips if the user ``is_staff``.

        :return: A list containing the deleted users.

        """
        deleted_users = []
        for user in self.filter(is_staff=False, is_active=False):
            if user.activation_key_expired():
                deleted_users.append(user)
                user.delete()
        return deleted_users


class EmailConfirmationManager(BaseManager):
    """
    E-mail address confirmation functionalities for User model.
    """

    def confirm_email(self, username, confirmation_key):
        """
        Confirm an email address by checking a ``confirmation_key``.

        A valid ``confirmation_key`` will set the newly wanted email address
        as the current email address. Returns the user after success or
        ``False`` when the confirmation key is invalid.

        :param username:
            String containing the unique username for verification.

        :param confirmation_key:
            String containing the secret SHA1 that is used for verification.

        :return:
            The verified :class:`User` or ``False`` if not successful.

        """
        if SHA1_RE.search(confirmation_key):
            try:
                user = self.select_related().get(
                    username=username,
                    email_confirmation_key=confirmation_key,
                    email_unconfirmed__isnull=False,
                )
            except self.model.DoesNotExist:
                return False
            else:
                user.email = user.email_unconfirmed
                user.email_unconfirmed, user.email_confirmation_key = "", ""
                user.save(using=self._db)
                # Send the CINFIRMATION_COMPLETE signal
                signals.CINFIRMATION_COMPLETE.send(sender=None, user=user)
                return user
        return False


class UserProfileManager(BaseManager):
    """
    Profile functionalities for User model.
    """

    def get_visible_profiles(self, user=None):
        """
        Returns all the visible profiles available to this user.

        For now keeps it simple by just applying the cases when a user is not
        active, a user has it's profile closed to everyone or a user only
        allows registered users to view their profile.

        :param user:
            A Django :class:`User` instance.

        :return:
            All profiles that are visible to this user.

        """
        profiles = self.select_related().all()

        filter_kwargs = {"is_active": True}

        profiles = profiles.filter(**filter_kwargs)
        if user and isinstance(user, AnonymousUser):
            profiles = []
        return profiles


# pylint: disable=bad-continuation
class BaseUserManager(
    AccountActivationManager, EmailConfirmationManager, UserProfileManager
):
    pass


class UserManager(BaseUserManager):
    """ Extra functionality for the User model. """
