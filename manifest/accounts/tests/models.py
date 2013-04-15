# -*- coding: utf-8 -*-
import re
import hashlib
import datetime

from django.core import mail
from django.conf import settings
from django.test import TestCase

from django.contrib.sites.models import Site
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser

from manifest.accounts import settings as accounts_settings
from manifest.accounts.models import upload_to_picture

from manifest.accounts.tests.profiles.tests import ProfileTestCase
from manifest.accounts.tests.profiles.models import Profile



class AccountModelTests(ProfileTestCase):
    """ Test the model of Account """
    user_info = {'username': 'foo',
                 'password': 'bar',
                 'email': 'foo@example.com'}

    fixtures = ['test']

    def test_upload_picture(self):
        """
        Test the uploaded path of pictures

        TODO: What if a image get's uploaded with no extension?

        """
        user = get_user_model().objects.get(pk=1)
        filename = 'my_avatar.png'
        path = upload_to_picture(user.profile, filename)

        # Path should be changed from the original
        self.failIfEqual(filename, path)

        # Check if the correct path is returned
        PICTURE_RE = re.compile('^%(picture_path)s/[a-f0-9]{10}.png$' %
                            {'picture_path': getattr(accounts_settings, 
                                'ACCOUNTS_PICTURE_PATH','%s/%s' % (
                                    str(user.profile._meta.app_label), 
                                    str(user.profile._meta.module_name)))})

        self.failUnless(PICTURE_RE.search(path))

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
        user.date_joined -= datetime.timedelta(days=accounts_settings.ACCOUNTS_ACTIVATION_DAYS + 1)
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


class ProfileBaseModelTest(ProfileTestCase):
    """ Test the ``ProfileBase`` model """
    fixtures = ['test']

    def test_picture_url(self):
        """ The user has uploaded it's own picture. This should be returned. """
        profile = Profile.objects.get(pk=1)
        profile.picture = 'fake_image.png'
        profile.save()

        profile = Profile.objects.get(pk=1)
        self.failUnlessEqual(profile.get_picture_url(),
                             settings.MEDIA_URL + 'fake_image.png')

    def test_stringification(self):
        """ Profile should return a human-readable name as an object """
        profile = Profile.objects.get(pk=1)
        self.failUnlessEqual(profile.__unicode__(),
                             'Profile of %s' % profile.user.username)

    def test_get_picture_url_without_gravatar(self):
        """
        Test if the correct picture is returned for the user when
        ``ACCOUNTS_PICTURE_GRAVATAR`` is set to ``False``.

        """
        # This user has no picture, and gravatar is disabled. And to make
        # matters worse, there isn't even a default image.
        accounts_settings.ACCOUNTS_GRAVATAR_PICTURE = False
        profile = Profile.objects.get(pk=1)
        self.failUnlessEqual(profile.get_picture_url(), None)

        # There _is_ a default image
        accounts_settings.ACCOUNTS_GRAVATAR_DEFAULT = 'http://example.com'
        profile = Profile.objects.get(pk=1)
        self.failUnlessEqual(profile.get_picture_url(), 'http://example.com')

        # Settings back to default
        accounts_settings.ACCOUNTS_PICTURE_GRAVATAR = True

    def test_get_picture_url_with_gravatar(self):
        """
        Test if the correct picture is returned when the user makes use of gravatar.

        """
        template = 'http://www.gravatar.com/avatar/%(hash)s?s=%(size)s&d=%(default)s'
        profile = Profile.objects.get(pk=1)

        gravatar_hash = hashlib.md5(profile.user.email).hexdigest()

        # Test with the default settings
        self.failUnlessEqual(profile.get_picture_url(),
                             template % {'hash': gravatar_hash,
                                         'size': accounts_settings.ACCOUNTS_GRAVATAR_SIZE,
                                         'default': accounts_settings.ACCOUNTS_GRAVATAR_DEFAULT})

        # Change accounts settings
        accounts_settings.ACCOUNTS_GRAVATAR_SIZE = 180
        accounts_settings.ACCOUNTS_GRAVATAR_DEFAULT = '404'

        self.failUnlessEqual(profile.get_picture_url(),
                             template % {'hash': gravatar_hash,
                                         'size': accounts_settings.ACCOUNTS_GRAVATAR_SIZE,
                                         'default': accounts_settings.ACCOUNTS_GRAVATAR_DEFAULT})

        # Settings back to default
        accounts_settings.ACCOUNTS_PICTURE_MAX_SIZE = 80
        accounts_settings.ACCOUNTS_GRAVATAR_DEFAULT = 'identicon'

    def test_get_full_name_or_username(self):
        """ Test if the full name or username are returned correcly """
        user = get_user_model().objects.get(pk=1)
        profile = user.get_profile()

        # Profile #1 has a first and last name
        full_name = profile.get_full_name_or_username()
        self.failUnlessEqual(full_name, "John Doe")

        # Let's empty out his name, now we should get his username
        user.first_name = ''
        user.last_name = ''
        user.save()

        self.failUnlessEqual(profile.get_full_name_or_username(),
                             "john")

        # Finally, accounts doesn't use any usernames, so we should return the
        # e-mail address.
        accounts_settings.ACCOUNTS_WITHOUT_USERNAMES = True
        self.failUnlessEqual(profile.get_full_name_or_username(),
                             "john@example.com")
        accounts_settings.ACCOUNTS_WITHOUT_USERNAMES = False
