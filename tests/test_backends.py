# -*- coding: utf-8 -*-
""" Manifest Backend Tests
"""

from django.contrib.auth import get_user_model

from manifest.backends import AuthenticationBackend
from tests.base import ManifestTestCase


class AuthenticationBackendTests(ManifestTestCase):
    """Tests for :class:`AuthenticationBackend
    <manifest.backends.AuthenticationBackend>` which should return
    a ``User`` object when a ``username`` or ``email``
    with correct ``password`` supplied.
    """

    backend = AuthenticationBackend()

    def test_with_username(self):
        """Should return ``User`` object if correct username and
        password supplied.
        """
        # Invalid usernames or passwords
        invalid_dicts = [
            # Invalid password
            {"identification": "john", "password": "invalid"},
            # Invalid username
            {"identification": "foo", "password": "pass"},
        ]
        for invalid_dict in invalid_dicts:
            result = self.backend.authenticate(
                request=None,
                identification=invalid_dict["identification"],
                password=invalid_dict["password"],
            )
            self.assertFalse(isinstance(result, get_user_model()))

        # Valid username and password
        valid_dict = {"identification": "john", "password": "pass"}
        result = self.backend.authenticate(
            request=None,
            identification=valid_dict["identification"],
            password=valid_dict["password"],
        )
        self.assertTrue(isinstance(result, get_user_model()))

    def test_with_email(self):
        """Should return ``User`` object if correct email and
        password supplied.
        """
        # Invalid e-mail adressses or passwords
        invalid_data_dicts = [
            # Invalid password
            {"identification": "john@example.com", "password": "invalid"},
            # Invalid e-mail address
            {"identification": "foo@example.com", "password": "pass"},
        ]
        for invalid_dict in invalid_data_dicts:
            result = self.backend.authenticate(
                request=None,
                identification=invalid_dict["identification"],
                password=invalid_dict["password"],
            )
            self.assertFalse(isinstance(result, get_user_model()))

        # Valid e-email address and password
        valid_dict = {"identification": "john@example.com", "password": "pass"}
        result = self.backend.authenticate(
            request=None,
            identification=valid_dict["identification"],
            password=valid_dict["password"],
        )
        self.assertTrue(isinstance(result, get_user_model()))

    def test_get_user(self):
        """Should return ``User`` object if user exists.
        """
        user = self.backend.get_user(1)
        self.assertEqual(user.username, "john")

        # None should be returned when false id.
        user = self.backend.get_user(99)
        self.assertFalse(user)
