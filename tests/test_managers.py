# -*- coding: utf-8 -*-
""" Manifest Model Manager Tests
"""

import datetime
import re

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser

from manifest import defaults
from tests.base import ManifestTestCase


class AccountActivationManagerTests(ManifestTestCase):
    """Tests for :class:`AccountActivationManager
    <manifest.managers.AccountActivationManager>`.
    """

    user_info = {
        "username": "foo",
        "password": "bar",
        "email": "foo@example.com",
    }

    fixtures = ["test"]

    def test_create_user(self):
        """The :func:`create_user
        <manifest.managers.AccountActivationManager.create_user>`
        method should create an inactive ``User`` object with
        an ``activation_key`` which will be used to activate
        the user account.
        """
        # Check that the fields are set.
        new_user = get_user_model().objects.create_user(**self.user_info)
        self.assertEqual(new_user.username, self.user_info["username"])
        self.assertEqual(new_user.email, self.user_info["email"])
        self.assertTrue(new_user.check_password(self.user_info["password"]))
        # User should be inactive
        self.assertFalse(new_user.is_active)
        # User has a valid SHA1 activation key
        self.assertTrue(re.match("^[a-f0-9]{40}$", new_user.activation_key))
        # User should be saved
        self.assertEqual(
            get_user_model()
            .objects.filter(email=self.user_info["email"])
            .count(),
            1,
        )

    def test_activate_user_valid(self):
        """The :func:`activate_user
        <manifest.managers.AccountActivationManager.activate_user>`
        method should activate the user if the key is valid, then
        set a label as new ``activation_key`` that is defined in
        ``MANIFEST_ACTIVATED_LABEL`` setting.
        """
        user = get_user_model().objects.create_user(**self.user_info)
        active_user = get_user_model().objects.activate_user(
            user.username, user.activation_key
        )
        # The returned user should be the same as the one just created.
        self.assertEqual(user, active_user)
        # The user should now be active.
        self.assertTrue(active_user.is_active)
        # The activation key should be the same as in the settings
        self.assertEqual(
            active_user.activation_key, defaults.MANIFEST_ACTIVATED_LABEL
        )

    def test_activate_user_invalid(self):
        """The :func:`activate_user
        <manifest.managers.AccountActivationManager.activate_user>`
        method should return ``False`` if the key is invalid.
        """
        # Wrong key
        self.assertFalse(
            get_user_model().objects.activate_user("john", "wrong_key")
        )
        # At least the right length
        invalid_key = 10 * "a1b2"
        self.assertFalse(
            get_user_model().objects.activate_user("john", invalid_key)
        )

    def test_activate_user_expired(self):
        """The :func:`activate_user
        <manifest.managers.AccountActivationManager.activate_user>`
        method should return ``False`` if the key is expired.
        """
        user = get_user_model().objects.create_user(**self.user_info)
        # Set the date that the key is created a day further away than allowed
        user.date_joined -= datetime.timedelta(
            days=defaults.MANIFEST_ACTIVATION_DAYS + 1
        )
        user.save()
        # Try to activate the user
        get_user_model().objects.activate_user(
            user.username, user.activation_key
        )
        active_user = get_user_model().objects.get(username="foo")
        # Account activation should have failed
        self.assertFalse(active_user.is_active)
        # The activation key should still be a hash
        self.assertEqual(user.activation_key, active_user.activation_key)

    def test_delete_expired_users(self):
        """The :func:`delete_expired_users
        <manifest.managers.AccountActivationManager.delete_expired_users>`
        method should delete users whose ``activation_key`` is expired.
        """
        expired_user = get_user_model().objects.create_user(**self.user_info)
        expired_user.date_joined -= datetime.timedelta(
            days=defaults.MANIFEST_ACTIVATION_DAYS + 1
        )
        expired_user.save()
        deleted_users = get_user_model().objects.delete_expired_users()
        self.assertEqual(deleted_users[0].username, "foo")


class EmailConfirmationManagerTests(ManifestTestCase):
    """Tests for :class:`EmailConfirmationManager
    <manifest.managers.EmailConfirmationManager>`.
    """

    def test_confirm_email_valid(self):
        """The :func:`confirm_email
        <manifest.managers.EmailConfirmationManager.confirm_email>`
        method should change users email if the key is valid.
        """
        new_email = "john@newexample.com"
        user = get_user_model().objects.get(pk=1)
        user.change_email(new_email)
        # Confirm email
        confirmed_user = get_user_model().objects.confirm_email(
            user.username, user.email_confirmation_key
        )
        self.assertEqual(user, confirmed_user)
        # Check the new email is set.
        self.assertEqual(confirmed_user.email, new_email)
        # ``email_new`` and ``email_verification_key`` should be empty
        self.assertFalse(confirmed_user.email_unconfirmed)
        self.assertFalse(confirmed_user.email_confirmation_key)

    def test_confirm_email_invalid(self):
        """The :func:`confirm_email
        <manifest.managers.EmailConfirmationManager.confirm_email>`
        method should return ``False`` if the key is invalid.
        """
        new_email = "john@newexample.com"
        user = get_user_model().objects.get(pk=1)
        user.change_email(new_email)
        # Verify email with wrong SHA1
        self.assertFalse(
            get_user_model().objects.confirm_email("john", "sha1")
        )
        # Correct SHA1, but non-existend in db.
        self.assertFalse(
            get_user_model().objects.confirm_email("john", 10 * "a1b2")
        )


class UserProfileManagerTests(ManifestTestCase):
    """Tests for :class:`UserProfileManager
    <manifest.managers.UserProfileManager>`.
    """

    def test_get_visible_profiles(self):
        """Should return list of profiles if user is authenticated.
        """
        user = get_user_model().objects.get(pk=1)
        profiles = get_user_model().objects.get_visible_profiles(user)
        self.assertTrue(len(profiles) >= 1)
        profiles = get_user_model().objects.get_visible_profiles(
            AnonymousUser()
        )
        self.assertTrue(len(profiles) == 0)
