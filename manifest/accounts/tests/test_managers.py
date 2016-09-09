# -*- coding: utf-8 -*-
import re
import datetime

from django.core import mail
from django.contrib.auth import get_user_model

from manifest.accounts import defaults
from manifest.accounts.tests.base import AccountsTestCase


class AccountManagerTests(AccountsTestCase):
    """ Test the manager of Accunts """
    user_info = {'username': 'foo',
                 'password': 'bar',
                 'email': 'foo@example.com'}

    fixtures = ['test']

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
        new_user = get_user_model().objects.create_user(**self.user_info)
        self.assertEqual(new_user.username, self.user_info['username'])
        self.assertEqual(new_user.email, self.user_info['email'])
        self.failUnless(new_user.check_password(self.user_info['password']))

        # User should be inactive
        self.failIf(new_user.is_active)

        # User has a valid SHA1 activation key
        self.failUnless(re.match('^[a-f0-9]{40}$', new_user.activation_key))

        # User should be saved
        self.failUnlessEqual(get_user_model().objects.filter(email=self.user_info['email']).count(), 1)

    def test_activation_valid(self):
        """
        Valid activation of an user.

        Activation of an user with a valid ``activation_key`` should activate
        the user and set a new invalid ``activation_key`` that is defined in
        the setting ``ACCOUNTS_ACTIVATED``.

        """
        user = get_user_model().objects.create_user(**self.user_info)
        active_user = get_user_model().objects.activate_user(user.username,
                                                          user.activation_key)

        # The returned user should be the same as the one just created.
        self.failUnlessEqual(user, active_user)

        # The user should now be active.
        self.failUnless(active_user.is_active)

        # The activation key should be the same as in the settings
        self.assertEqual(active_user.activation_key,
                         defaults.ACCOUNTS_ACTIVATED)

    def test_activation_invalid(self):
        """
        Activation with a key that's invalid should make
        ``Account.objects.activate_user`` return ``False``.

        """
        # Wrong key
        self.failIf(get_user_model().objects.activate_user('john', 'wrong_key'))

        # At least the right length
        invalid_key = 10 * 'a1b2'
        self.failIf(get_user_model().objects.activate_user('john', invalid_key))

    def test_activation_expired(self):
        """
        Activation with a key that's expired should also make
        ``Account.objects.activation_user`` return ``False``.

        """
        user = get_user_model().objects.create_user(**self.user_info)

        # Set the date that the key is created a day further away than allowed
        user.date_joined -= datetime.timedelta(days=defaults.ACCOUNTS_ACTIVATION_DAYS + 1)
        user.save()

        # Try to activate the user
        get_user_model().objects.activate_user(user.username, user.activation_key)

        active_user = get_user_model().objects.get(username='foo')

        # Account activation should have failed
        self.failIf(active_user.is_active)

        # The activation key should still be a hash
        self.assertEqual(user.activation_key,
                         active_user.activation_key)

    def test_confirmation_valid(self):
        """
        Confirmation of a new e-mail address with turns out to be valid.

        """
        new_email = 'john@newexample.com'
        user = get_user_model().objects.get(pk=1)
        user.change_email(new_email)

        # Confirm email
        confirmed_user = get_user_model().objects.confirm_email(user.username,
                                                       user.email_confirmation_key)
        self.failUnlessEqual(user, confirmed_user)

        # Check the new email is set.
        self.failUnlessEqual(confirmed_user.email, new_email)

        # ``email_new`` and ``email_verification_key`` should be empty
        self.failIf(confirmed_user.email_unconfirmed)
        self.failIf(confirmed_user.email_confirmation_key)

    def test_confirmation_invalid(self):
        """
        Trying to confirm a new e-mail address when the ``confirmation_key``
        is invalid.

        """
        new_email = 'john@newexample.com'
        user = get_user_model().objects.get(pk=1)
        user.change_email(new_email)

        # Verify email with wrong SHA1
        self.failIf(get_user_model().objects.confirm_email('john', 'sha1'))

        # Correct SHA1, but non-existend in db.
        self.failIf(get_user_model().objects.confirm_email('john', 10 * 'a1b2'))

    def test_delete_expired_users(self):
        """
        Test if expired users are deleted from the datamanifest.accounts.tests.test_base.

        """
        expired_user = get_user_model().objects.create_user(**self.user_info)
        expired_user.date_joined -= datetime.timedelta(days=defaults.ACCOUNTS_ACTIVATION_DAYS + 1)
        expired_user.save()

        deleted_users = get_user_model().objects.delete_expired_users()

        self.failUnlessEqual(deleted_users[0].username, 'foo')