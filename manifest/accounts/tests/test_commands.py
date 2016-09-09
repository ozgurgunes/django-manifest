# -*- coding: utf-8 -*-
from django.core.management import call_command
from django.contrib.auth import get_user_model

from manifest.accounts import defaults
from manifest.accounts.tests.base import AccountsTestCase

import datetime


class CleanExpiredTests(AccountsTestCase):
    user_info = {'username': 'alice',
                 'password': 'swordfish',
                 'email': 'alice@example.com'}

    def test_clean_expired(self):
        """
        Test if ``clean_expired`` deletes all users which ``activation_key``
        is expired.

        """
        # Create an account which is expired.
        user = get_user_model().objects.create_user(**self.user_info)
        user.date_joined -= datetime.timedelta(days=defaults.ACCOUNTS_ACTIVATION_DAYS + 1)
        user.save()

        # There should be one account now
        get_user_model().objects.get(username=self.user_info['username'])

        # Clean it.
        call_command('clean_expired')

        self.failUnlessEqual(get_user_model().objects.filter(username=self.user_info['username']).count(), 0)
