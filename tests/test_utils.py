# -*- coding: utf-8 -*-
""" Manifest Utility Tests
"""

import hashlib

from manifest import defaults
from manifest.utils import get_gravatar, get_login_redirect, get_protocol
from tests.base import ManifestTestCase


class UtilsTests(ManifestTestCase):
    """Tests for :mod:`utils <manifest.utils>`.
    """

    fixtures = ["test"]

    def test_get_gravatar(self):
        """Should return appropriate Gravatar.
        """
        template = (
            "http://www.gravatar.com/avatar/%(hash)s?s=%(size)s&d=%(type)s"
        )
        # The hash for alice@example.com
        key = hashlib.md5("alice@example.com".encode("utf-8")).hexdigest()
        # Check HTTP.
        self.assertEqual(
            get_gravatar("alice@example.com"),
            template
            % {
                "hash": key,
                "size": defaults.MANIFEST_AVATAR_SIZE,
                "type": defaults.MANIFEST_GRAVATAR_DEFAULT,
            },
        )
        # Test the switch to HTTPS.
        with self.defaults(MANIFEST_USE_HTTPS=True):
            template = "https://www.gravatar.com/avatar/"
            template += "%(hash)s?s=%(size)s&d=%(type)s"
            self.assertEqual(
                get_gravatar("alice@example.com"),
                template
                % {
                    "hash": key,
                    "size": defaults.MANIFEST_AVATAR_SIZE,
                    "type": defaults.MANIFEST_GRAVATAR_DEFAULT,
                },
            )

    def test_login_redirect(self):
        """Test ``login_redirect`` which should redirect the user
        after a succesfull signin.
        """
        # Test with ``redirect`` parameter.
        self.assertEqual(get_login_redirect(redirect="/acounts/"), "/acounts/")
        # Test without ``redirect`` paramter.
        self.assertEqual(
            get_login_redirect(), defaults.MANIFEST_LOGIN_REDIRECT_URL
        )

    def test_get_protocol(self):
        """Test if the correct protocol is returned
        """
        self.assertEqual(get_protocol(), "http")
        with self.settings(MANIFEST_USE_HTTPS=True):
            self.assertEqual(get_protocol(), "https")
