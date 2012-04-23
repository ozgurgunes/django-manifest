# -*- coding: utf-8 -*-
import re, datetime
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User, UserManager, Permission, AnonymousUser
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext as _

from manifest.accounts import settings as accounts_settings
from manifest.accounts import signals as accounts_signals
from manifest.accounts.utils import generate_sha1, get_profile_model

SHA1_RE = re.compile('^[a-f0-9]{40}$')

class AccountsManager(UserManager):
    """ Extra functionality for the Accounts model. """

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
            on a link in an e-mail. Defauts to ``True``.

        :param send_email:
            Boolean that defines if the user should be send an email. You could
            set this to ``False`` when you want to create a user in your own
            code, but don't want the user to activate through email.

        :return: :class:`User` instance representing the new user.

        """

        new_user = User.objects.create_user(username, email, password)
        new_user.is_active = active
        new_user.save()

        new_account = self.create_account(new_user)

        if send_email:
            new_account.send_activation_email()
 
        return new_user

    def create_account(self, user):
        """
        Creates both :class:`Account` and :class:`Profile` instances for this user.

        :param user:
            Django :class:`User` instance.

        :return: The newly created :class:`Account` instance.

        """
        # Create profile first
        new_profile = self.create_profile(user)

        # Create and reurn new account
        if isinstance(user.username, unicode):
            user.username = user.username.encode('utf-8')
        salt, activation_key = generate_sha1(user.username)
        return self.create(user=user, activation_key=activation_key)

    def create_profile(self, user):
        """
        Creates a :class:`Profile` instance for this user        

        :param user:
            Django :class:`User` instance.

        :return: The newly created :class:`Profile` instance.

        """
        # All users have an empty profile
        profile_model = get_profile_model()
        try:
            new_profile = user.get_profile()
        except profile_model.DoesNotExist:
            new_profile = profile_model(user=user)
            new_profile.save(using=self._db)
        return new_profile

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
                account = self.get(activation_key=activation_key)
            except self.model.DoesNotExist:
                return False
            if not account.activation_key_expired():
                account.activation_key = accounts_settings.ACCOUNTS_ACTIVATED
                user = account.user
                user.is_active = True
                account.save(using=self._db)
                user.save(using=self._db)

                # Send the activation_complete signal
                accounts_signals.activation_complete.send(sender=None, user=user)
                return user
        return False

    def confirm_email(self, confirmation_key):
        """
        Confirm an email address by checking a ``confirmation_key``.

        A valid ``confirmation_key`` will set the newly wanted e-mail address
        as the current e-mail address. Returns the user after success or
        ``False`` when the confirmation key is invalid.

        :param confirmation_key:
            String containing the secret SHA1 that is used for verification.

        :return:
            The verified :class:`User` or ``False`` if not successful.

        """
        if SHA1_RE.search(confirmation_key):
            try:
                account = self.get(email_confirmation_key=confirmation_key,
                                   email_unconfirmed__isnull=False)
            except self.model.DoesNotExist:
                return False
            else:
                user = account.user
                user.email = account.email_unconfirmed
                account.email_unconfirmed, account.email_confirmation_key = '',''
                account.save(using=self._db)
                user.save(using=self._db)

                # Send the confirmation_complete signal
                accounts_signals.confirmation_complete.send(sender=None, user=user)
                return user
        return False

    def delete_expired_users(self):
        """
        Checks for expired users and delete's the ``User`` associated with
        it. Skips if the user ``is_staff``.

        :return: A list containing the deleted users.

        """
        deleted_users = []
        for user in User.objects.filter(is_staff=False, is_active=False):
            if user.account.activation_key_expired():
                deleted_users.append(user)
                user.delete()
        return deleted_users

    def check_permissions(self):
        """
        Checks that all permissions are set correctly for the users.

        :return: A set of users whose permissions was wrong.

        """
        # Variable to supply some feedback
        changed_permissions = []
        changed_users = []
        warnings = []

        # Check that all the permissions are available.
        for model, perms in ASSIGNED_PERMISSIONS.items():
            if model == 'profile':
                model_obj = get_profile_model()
            else: model_obj = User
            model_content_type = ContentType.objects.get_for_model(model_obj)
            for perm in perms:
                try:
                    Permission.objects.get(codename=perm[0],
                                           content_type=model_content_type)
                except Permission.DoesNotExist:
                    changed_permissions.append(perm[1])
                    Permission.objects.create(name=perm[1],
                                              codename=perm[0],
                                              content_type=model_content_type)

        for user in User.objects.all():
            if not user.username == 'AnonymousUser':
                try:
                    user_profile = user.get_profile()
                except get_profile_model().DoesNotExist:
                    warnings.append(_("No profile found for %(username)s") \
                                        % {'username': user.username})
                else:
                    all_permissions = get_perms(user, user_profile) + get_perms(user, user)

                    for model, perms in ASSIGNED_PERMISSIONS.items():
                        if model == 'profile':
                            perm_object = user.get_profile()
                        else: perm_object = user

                        for perm in perms:
                            if perm[0] not in all_permissions:
                                assign(perm[0], user, perm_object)
                                changed_users.append(user)

        return (changed_permissions, changed_users, warnings)

class ProfileBaseManager(models.Manager):
    """
    Manager for :class: `ProfileBase`
    
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
        profiles = self.all()

        filter_kwargs = {'user__is_active': True}

        profiles = profiles.filter(**filter_kwargs)
        if user and isinstance(user, AnonymousUser):
            profiles = profiles.filter(user=user)
        return profiles

class ContactLookup(object):
    def get_query(self,q,request):
        """
        Return a query set.  you also have access to request.user if needed
        
        """
        return User.objects.filter(username__startswith=q)

    def format_result(self,user):
        # The search results display in the dropdown menu.  may contain html and multiple-lines. will remove any |  """
        return u"%s" % (user)

    def format_item(self,user):
        # The display of a currently selected object in the area below the search box. html is OK """
        return unicode(user)

    def get_objects(self):
        # Given a list of ids, return the objects ordered as you would like them on the admin page.
        # This is for displaying the currently selected items (in the case of a ManyToMany field)
        return User.objects.all()
