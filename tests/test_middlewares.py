# -*- coding: utf-8 -*-
""" Manifest Middleware Tests
"""

from django.contrib.auth import get_user_model
from django.http import HttpRequest

from manifest.middlewares import LocaleMiddleware
from tests.base import ManifestTestCase


class LocaleMiddlewareTests(ManifestTestCase):
    """Tests for :class:`LocaleMiddleware
    <manifest.middlewares.LocaleMiddleware>`.
    """

    fixtures = ["test"]

    def _get_request_with_user(self, user):
        """Returns a fake request with user.
        """
        request = HttpRequest()
        request.META = {"SERVER_NAME": "testserver", "SERVER_PORT": 80}
        request.method = "GET"
        request.session = {}
        # Add user
        request.user = user
        self.assertTrue(request)
        return request

    def test_preference_user(self):
        """Test the language preference of two users.
        """
        users = ((1, "tr-tr"), (2, "en-us"))

        for pk, lang in users:  # pylint: disable=invalid-name
            user = get_user_model().objects.get(pk=pk)
            request = self._get_request_with_user(user)
            # Check that the user has this preference
            self.assertEqual(user.locale, lang)
            # Request should have a ``LANGUAGE_CODE`` with dutch
            LocaleMiddleware().process_request(request)
            # pylint: disable=no-member
            self.assertEqual(request.LANGUAGE_CODE, lang)

    def test_without_language_field(self):
        """Middleware should do nothing if the profile has no language field.
        """
        with self.defaults(MANIFEST_LOCALE_FIELD="non_existant_language_field"):
            user = get_user_model().objects.get(pk=1)
            req = self._get_request_with_user(user)
            # Middleware should do nothing
            LocaleMiddleware().process_request(req)
            self.assertFalse(hasattr(req, "LANGUAGE_CODE"))
