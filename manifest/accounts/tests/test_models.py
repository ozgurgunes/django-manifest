# -*- coding: utf-8 -*-
import re
import hashlib
import datetime

from django.core import mail
from django.conf import settings

from django.contrib.sites.models import Site
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser

from manifest.accounts import defaults
from manifest.accounts.models import upload_to_picture
from manifest.accounts.tests.base import AccountsTestCase


class AccountModelTests(AccountsTestCase):
    """ Test the model of Account """
    user_info = {'username': 'foo',
                 'password': 'bar',
                 'email': 'foo@example.com'}

    fixtures = ['test']

    def test_change_email(self):
        """ TODO """
        pass

    def test_activation_expired_account(self):
        """
        ``Account.activation_key_expired()`` is ``True`` when the
        ``activation_key_created`` is more days ago than defined in
        ``ACCOUNTS_ACTIVATION_DAYS``.

        """
        user = get_user_model().objects.create_user(**self.user_info)
        user.date_joined -= datetime.timedelta(days=defaults.ACCOUNTS_ACTIVATION_DAYS + 1)
        user.save()

        user = get_user_model().objects.get(username='foo')
        self.failUnless(user.activation_key_expired())

    def test_activation_used_account(self):
        """
        An user cannot be activated anymore once the activation key is
        already used.

        """
        user = get_user_model().objects.create_user(**self.user_info)
        activated_user = get_user_model().objects.activate_user(user.username,
                                                             user.activation_key)
        self.failUnless(activated_user.activation_key_expired())

    def test_activation_unexpired_account(self):
        """
        ``Account.activation_key_expired()`` is ``False`` when the
        ``activation_key_created`` is within the defined timeframe.``

        """
        user = get_user_model().objects.create_user(**self.user_info)
        self.failIf(user.activation_key_expired())

    def test_activation_email(self):
        """
        When a new account is created, a activation e-mail should be send out
        by ``Account.send_activation_email``.

        """
        new_user = get_user_model().objects.create_user(**self.user_info)
        self.failUnlessEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.user_info['email']])


    def test_upload_picture(self):
        """
        Test the uploaded path of pictures

        TODO: What if a image get's uploaded with no extension?

        """
        user = get_user_model().objects.get(pk=1)
        filename = 'my_avatar.png'
        path = upload_to_picture(user, filename)

        # Path should be changed from the original
        self.failIfEqual(filename, path)

        # Check if the correct path is returned
        PICTURE_RE = re.compile('^%(picture_path)s/[a-f0-9]{10}.png$' %
                            {'picture_path': getattr(defaults, 
                                'ACCOUNTS_PICTURE_PATH','%s/%s' % (
                                    str(user._meta.app_label), 
                                    str(user._meta.model_name)))})

        self.failUnless(PICTURE_RE.search(path))

    def test_picture_url(self):
        """ The user has uploaded it's own picture. This should be returned. """
        filename = 'fake_image.png'
        user = get_user_model().objects.get(pk=1)
        user.picture = filename
        user.save()
        self.failUnlessEqual(user.get_picture_url(),
                             settings.MEDIA_URL + filename)

    def test_get_picture_url_without_gravatar(self):
        """
        Test if the correct picture is returned for the user when
        ``ACCOUNTS_PICTURE_GRAVATAR`` is set to ``False``.

        """
        user = get_user_model().objects.get(pk=1)
        # This user has no picture, and gravatar is disabled. And to make
        # matters worse, there isn't even a default image.
        defaults.ACCOUNTS_GRAVATAR_PICTURE = False
        self.failUnlessEqual(user.get_picture_url(), None)

        # There _is_ a default image
        defaults.ACCOUNTS_GRAVATAR_DEFAULT = 'http://example.com'
        self.failUnlessEqual(user.get_picture_url(), 'http://example.com')

        # Settings back to default
        defaults.ACCOUNTS_PICTURE_GRAVATAR = True

    def test_get_picture_url_with_gravatar(self):
        """
        Test if the correct picture is returned when the user makes use of gravatar.

        """
        template = 'http://www.gravatar.com/avatar/%(hash)s?s=%(size)s&d=%(default)s'
        user = get_user_model().objects.get(pk=1)

        gravatar_hash = hashlib.md5(user.email).hexdigest()

        # Test with the default settings
        self.failUnlessEqual(user.get_picture_url(),
                             template % {'hash': gravatar_hash,
                                         'size': defaults.ACCOUNTS_GRAVATAR_SIZE,
                                         'default': defaults.ACCOUNTS_GRAVATAR_DEFAULT})

        # Change accounts settings
        defaults.ACCOUNTS_GRAVATAR_SIZE = 180
        defaults.ACCOUNTS_GRAVATAR_DEFAULT = '404'

        self.failUnlessEqual(user.get_picture_url(),
                             template % {'hash': gravatar_hash,
                                         'size': defaults.ACCOUNTS_GRAVATAR_SIZE,
                                         'default': defaults.ACCOUNTS_GRAVATAR_DEFAULT})

        # Settings back to default
        defaults.ACCOUNTS_PICTURE_MAX_SIZE = 80
        defaults.ACCOUNTS_GRAVATAR_DEFAULT = 'identicon'

    def test_get_full_name_or_username(self):
        """ Test if the full name or username are returned correcly """
        user = get_user_model().objects.get(pk=1)

        # Profile #1 has a first and last name
        full_name = user.get_full_name_or_username()
        self.failUnlessEqual(full_name, "John Doe")

        # Let's empty out his name, now we should get his username
        user.first_name = ''
        user.last_name = ''
        user.save()

        self.failUnlessEqual(user.get_full_name_or_username(),
                             "john")

        # Finally, accounts doesn't use any usernames, so we should return the
        # e-mail address.
        defaults.ACCOUNTS_WITHOUT_USERNAMES = True
        self.failUnlessEqual(user.get_full_name_or_username(),
                             "john@example.com")
        defaults.ACCOUNTS_WITHOUT_USERNAMES = False
