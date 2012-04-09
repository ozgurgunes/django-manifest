from django.test import TestCase
from django.core.urlresolvers import reverse

from manifest.accounts.utils import get_gravatar
from manifest.accounts import settings as accounts_settings

import re

class DecoratorTests(TestCase):
    """ Test the decorators """

    def test_secure_required(self):
        """
        Test that the ``secure_required`` decorator does a permanent redirect
        to a secured page.

        """
        accounts_settings.ACCOUNTS_USE_HTTPS = True
        response = self.client.get(reverse('accounts_login'))

        # Test for the permanent redirect
        self.assertEqual(response.status_code, 301)

        # Test if the redirected url contains 'https'. Couldn't use
        # ``assertRedirects`` here because the redirected to page is
        # non-existant.
        self.assertTrue('https' in str(response))

        # Set back to the old settings
        accounts_settings.ACCOUNTS_USE_HTTPS = False
