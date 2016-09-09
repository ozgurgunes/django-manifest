# -*- coding: utf-8 -*-
import hashlib

from django.conf import settings
from django.contrib.auth import get_user_model

from manifest.accounts.utils import (get_gravatar, login_redirect,
                           get_protocol)
from manifest.accounts import defaults
from manifest.accounts.tests.base import AccountsTestCase

class UtilsTests(AccountsTestCase):
    """ Test the extra utils methods """
    fixtures = ['test']

    def test_get_gravatar(self):
        template = 'http://www.gravatar.com/avatar/%(hash)s?s=%(size)s&d=%(type)s'

        # The hash for alice@example.com
        hash = hashlib.md5('alice@example.com').hexdigest()

        # Check the defaults.
        self.failUnlessEqual(get_gravatar('alice@example.com'),
                             template % {'hash': hash,
                                         'size': 80,
                                         'type': 'identicon'})

        # Check different size
        self.failUnlessEqual(get_gravatar('alice@example.com', size=200),
                             template % {'hash': hash,
                                         'size': 200,
                                         'type': 'identicon'})

        # Check different default
        http_404 = get_gravatar('alice@example.com', default='404')
        self.failUnlessEqual(http_404,
                             template % {'hash': hash,
                                         'size': 80,
                                         'type': '404'})

        # Is it really a 404?
        response = self.client.get(http_404)
        self.failUnlessEqual(response.status_code, 404)

        # Test the switch to HTTPS
        defaults.ACCOUNTS_GRAVATAR_SECURE = True

        template = 'https://secure.gravatar.com/avatar/%(hash)s?s=%(size)s&d=%(type)s'
        self.failUnlessEqual(get_gravatar('alice@example.com'),
                             template % {'hash': hash,
                                         'size': 80,
                                         'type': 'identicon'})

        # And set back to default
        defaults.ACCOUNTS_GRAVATAR_SECURE = False

    def test_login_redirect(self):
        """
        Test redirect function which should redirect the user after a
        succesfull signin.

        """
        # Test with a requested redirect
        self.failUnlessEqual(login_redirect(redirect='/accounts/'), '/accounts/')

        # Test with only the user specified
        user = get_user_model().objects.get(pk=1)
        self.failUnlessEqual(login_redirect(user=user),
                             '/profiles/%s/' % user.username)
        
        # The ultimate fallback, probably never used
        self.failUnlessEqual(login_redirect(), settings.LOGIN_REDIRECT_URL)

    def test_get_protocol(self):
        """ Test if the correct protocol is returned """
        self.failUnlessEqual(get_protocol(), 'http')

        defaults.ACCOUNTS_USE_HTTPS = True
        self.failUnlessEqual(get_protocol(), 'https')
        defaults.ACCOUNTS_USE_HTTPS = False