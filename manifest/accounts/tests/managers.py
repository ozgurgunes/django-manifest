from django.test import TestCase
from django.core import mail
from django.contrib.auth.models import User

from manifest.accounts.models import Account
from manifest.accounts import settings as accounts_settings

from guardian.shortcuts import get_perms

import datetime, re

class AccountsManagerTests(TestCase):
    """ Test the manager of Accounts """
    user_info = {'username': 'alice',
                 'password': 'swordfish',
                 'email': 'alice@example.com'}

    fixtures = ['users']

    def test_create_inactive_user(self):
        """
        Test the creation of a new user.

        ``Account.create_inactive_user`` should create a new user that is
        not active. The user should get an ``activation_key`` that is used to
        set the user as active.

        Every user also has a profile, so this method should create an empty
        profile.

        """
        # Check that the fields are set.
        new_user = Account.objects.create_user(**self.user_info)
        self.assertEqual(new_user.username, self.user_info['username'])
        self.assertEqual(new_user.email, self.user_info['email'])
        self.failUnless(new_user.check_password(self.user_info['password']))

        # User should be inactive
        self.failIf(new_user.is_active)

        # User has a valid SHA1 activation key
        self.failUnless(re.match('^[a-f0-9]{40}$', new_user.account.activation_key))

        # User now has an profile.
        self.failUnless(new_user.get_profile())

        # User should be saved
        self.failUnlessEqual(User.objects.filter(email=self.user_info['email']).count(), 1)

    def test_activation_valid(self):
        """
        Valid activation of an user.

        Activation of an user with a valid ``activation_key`` should activate
        the user and set a new invalid ``activation_key`` that is defined in
        the setting ``ACCOUNTS_ACTIVATED``.

        """
        user = Account.objects.create_user(**self.user_info)
        active_user = Account.objects.activate_user(user.username,
                                                          user.account.activation_key)

        # The returned user should be the same as the one just created.
        self.failUnlessEqual(user, active_user)

        # The user should now be active.
        self.failUnless(active_user.is_active)

        # The user should have permission to view and change its profile
        self.failUnless('view_profile' in get_perms(active_user, active_user.get_profile()))
        self.failUnless('change_profile' in get_perms(active_user, active_user.get_profile()))

        # The activation key should be the same as in the settings
        self.assertEqual(active_user.account.activation_key,
                         accounts_settings.ACCOUNTS_ACTIVATED)

    def test_activation_invalid(self):
        """
        Activation with a key that's invalid should make
        ``Account.objects.activate_user`` return ``False``.

        """
        # Wrong key
        self.failIf(Account.objects.activate_user('john', 'wrong_key'))

        # At least the right length
        invalid_key = 10 * 'a1b2'
        self.failIf(Account.objects.activate_user('john', invalid_key))

    def test_activation_expired(self):
        """
        Activation with a key that's expired should also make
        ``Account.objects.activation_user`` return ``False``.

        """
        user = Account.objects.create_user(**self.user_info)

        # Set the date that the key is created a day further away than allowed
        user.date_joined -= datetime.timedelta(days=accounts_settings.ACCOUNTS_ACTIVATION_DAYS + 1)
        user.save()

        # Try to activate the user
        Account.objects.activate_user(user.username, user.account.activation_key)

        active_user = User.objects.get(username='alice')

        # Account activation should have failed
        self.failIf(active_user.is_active)

        # The activation key should still be a hash
        self.assertEqual(user.account.activation_key,
                         active_user.account.activation_key)

    def test_confirmation_valid(self):
        """
        Confirmation of a new e-mail address with turns out to be valid.

        """
        new_email = 'john@newexample.com'
        user = User.objects.get(pk=1)
        user.account.change_email(new_email)

        # Confirm email
        confirmed_user = Account.objects.confirm_email(user.username,
                                                       user.account.email_confirmation_key)
        self.failUnlessEqual(user, confirmed_user)

        # Check the new email is set.
        self.failUnlessEqual(confirmed_user.email, new_email)

        # ``email_new`` and ``email_verification_key`` should be empty
        self.failIf(confirmed_user.account.email_unconfirmed)
        self.failIf(confirmed_user.account.email_confirmation_key)

    def test_confirmation_invalid(self):
        """
        Trying to confirm a new e-mail address when the ``confirmation_key``
        is invalid.

        """
        new_email = 'john@newexample.com'
        user = User.objects.get(pk=1)
        user.account.change_email(new_email)

        # Verify email with wrong SHA1
        self.failIf(Account.objects.confirm_email('john', 'sha1'))

        # Correct SHA1, but non-existend in db.
        self.failIf(Account.objects.confirm_email('john', 10 * 'a1b2'))

    def test_delete_expired_users(self):
        """
        Test if expired users are deleted from the database.

        """
        expired_user = Account.objects.create_user(**self.user_info)
        expired_user.date_joined -= datetime.timedelta(days=accounts_settings.ACCOUNTS_ACTIVATION_DAYS + 1)
        expired_user.save()

        deleted_users = Account.objects.delete_expired_users()

        self.failUnlessEqual(deleted_users[0].username, 'alice')
