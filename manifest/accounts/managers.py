# -*- coding: utf-8 -*-
import re, datetime
from django.db import models
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.contrib.auth.models import UserManager as BaseManager, AnonymousUser
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext as _

from manifest.accounts import defaults
from manifest.accounts import signals as accounts_signals
from manifest.accounts.utils import generate_sha1


SHA1_RE = re.compile('^[a-f0-9]{40}$')


class AccountActivationManager(BaseManager):
    """
    Registration and account activation functionalities for User model.
    """
    
    def create_user(self, username, email, password, active=False,
                    send_email=True):
        """
        A simple wrapper that creates a new :class:`User`.

        :param username:
            String containing the username of the new user.

        :param email:
            String containing the email address of the new user.

        :param password:
            String containing the password for the new user.

        :param active:
            Boolean that defines if the user requires activation by clicking 
            on a link in an email. Defauts to ``True``.

        :param send_email:
            Boolean that defines if the user should be send an email. You 
            could set this to ``False`` when you want to create a user in 
            your own code, but don't want the user to activate through email.

        :return: :class:`User` instance representing the new user.

        """

        user = super(AccountActivationManager, self).create_user(username, email, password)

        if isinstance(user.username, unicode):
            username = user.username.encode('utf-8')
        salt, activation_key = generate_sha1(username)
        user.is_active = active
        user.activation_key = activation_key
        user.save(using=self._db)

        if send_email:
            user.send_activation_email()
 
        return user

    def activate_user(self, username, activation_key):
        """
        Activate an :class:`User` by supplying a valid ``activation_key``.

        If the key is valid and an user is found, activates the user and
        return it. Also sends the ``activation_complete`` signal.

        :param activation_key:
            String containing the secret SHA1 for a valid activation.

        :return:
            The newly activated :class:`User` or ``False`` if not successful.

        """
        if SHA1_RE.search(activation_key):
            try:
                user = self.get(activation_key=activation_key)
            except self.model.DoesNotExist:
                return False
            if not user.activation_key_expired():
                user.activation_key = defaults.ACCOUNTS_ACTIVATED
                user.is_active = True
                user.save(using=self._db)
                # Send the activation_complete signal
                accounts_signals.activation_complete.send(sender=None, 
                    user=user)
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

        :param confirmation_key:
            String containing the secret SHA1 that is used for verification.

        :return:
            The verified :class:`User` or ``False`` if not successful.

        """
        if SHA1_RE.search(confirmation_key):
            try:
                user = self.select_related().get(username=username,
                                    email_confirmation_key=confirmation_key,
                                    email_unconfirmed__isnull=False)
            except self.model.DoesNotExist:
                return False
            else:
                user.email = user.email_unconfirmed
                user.email_unconfirmed, user.email_confirmation_key = '',''
                user.save(using=self._db)
                # Send the confirmation_complete signal
                accounts_signals.confirmation_complete.send(sender=None, 
                    user=user)
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

        filter_kwargs = {'is_active': True}

        profiles = profiles.filter(**filter_kwargs)
        if user and isinstance(user, AnonymousUser):
            profiles = []
        return profiles


class BaseUserManager(AccountActivationManager,
                        EmailConfirmationManager,
                        UserProfileManager):
    pass



class UserManager(BaseUserManager):
    """ Extra functionality for the User model. """
    pass