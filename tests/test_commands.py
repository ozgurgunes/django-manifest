# -*- coding: utf-8 -*-
""" Manifest Management Command Tests
"""

import datetime

from django.contrib.auth import get_user_model
from django.core.management import call_command

from manifest import defaults
from tests.base import ManifestTestCase

USER_MODEL = get_user_model()


class CleanExpiredTests(ManifestTestCase):
    """Tests for :mod:`clean_expired
    <manifest.management.commands.clean_expired>`.
    """

    user_info = {
        "username": "alice",
        "password": "swordfish",
        "email": "alice@example.com",
    }

    def test_clean_expired(self):
        """Should delete all users whose ``activation_key`` is expired.
        """
        # Create an account which is expired.
        user = USER_MODEL.objects.create_user(**self.user_info)
        user.date_joined -= datetime.timedelta(
            days=defaults.MANIFEST_ACTIVATION_DAYS + 1
        )
        user.save()
        # There should be one account now
        USER_MODEL.objects.get(username=self.user_info["username"])
        # Clean it.
        call_command("clean_expired")
        self.assertEqual(
            USER_MODEL.objects.filter(
                username=self.user_info["username"]
            ).count(),
            0,
        )
