# -*- coding: utf-8 -*-
""" Manifest Decorator Tests
"""

from django.urls import reverse

from tests.base import ManifestTestCase


class DecoratorTests(ManifestTestCase):
    """Tests for :mod:`decorators <manifest.decorators>`.
    """

    def test_secure_required(self):
        """Should redirect to secured version of page
        if ``MANIFEST_USE_HTTPS`` setting is ``True``.
        """

        # Set true
        with self.defaults(MANIFEST_USE_HTTPS=True):
            response = self.client.get(reverse("auth_login"))
            # Test for the permanent redirect
            self.assertEqual(response.status_code, 301)
            # Test if the redirected url contains 'https'. Couldn't use
            # ``assertRedirects`` here because the redirected to page is
            # non-existant.
            self.assertTrue("https" in response.get("Location"))
