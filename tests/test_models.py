# -*- coding: utf-8 -*-
""" Manifest Model Tests
"""

import datetime
import hashlib
import re

from django.conf import settings
from django.contrib.auth import get_user_model

from manifest import defaults
from manifest.utils import get_image_path
from tests.base import ManifestUploadTestCase


class UserModelTests(ManifestUploadTestCase):
    """Tests for :class:`User <manifest.models.User>`.
    """

    user_info = {
        "username": "alice",
        "password": "wonderland",
        "email": "alice@example.com",
    }

    fixtures = ["test"]

    def test_change_email(self):
        """TODO
        """

    def test_absolute_url(self):
        """Path for ``user_detail`` with users username.
        """
        user = get_user_model().objects.get(pk=1)
        self.assertEqual(
            user.get_absolute_url(),
            ("user_detail", None, {"username": user.username}),
        )

    def test_activation_expired_account(self):
        """The :func:`activation_key_expired
        <manifest.models.Account.activation_key_expired>` method
        should return ``True`` if the ``activation_key_created``
        is older than defined in ``MANIFEST_ACTIVATION_DAYS``.
        """
        user = get_user_model().objects.create_user(**self.user_info)
        user.date_joined -= datetime.timedelta(
            days=defaults.MANIFEST_ACTIVATION_DAYS + 1
        )
        user.save()
        user = get_user_model().objects.get(
            username=self.user_info["username"]
        )
        self.assertTrue(user.activation_key_expired())

    def test_activation_used_account(self):
        """A user cannot be activated anymore once the activation key is
        already used.
        """
        user = get_user_model().objects.create_user(**self.user_info)
        activated_user = get_user_model().objects.activate_user(
            user.username, user.activation_key
        )
        self.assertTrue(activated_user.activation_key_expired())

    def test_activation_unexpired_account(self):
        """The :func:`activation_key_expired
        <manifest.models.Account.activation_key_expired>` method
        should return ``False`` if the ``activation_key_created``
        is within the defined timeframe.
        """
        user = get_user_model().objects.create_user(**self.user_info)
        self.assertFalse(user.activation_key_expired())

    def test_user_age(self):
        # Should return relative time delta regarding user's birth date.
        user = get_user_model().objects.get(pk=1)
        age = str(datetime.datetime.now().year - user.birth_date.year)
        self.assertEqual(user.age, age)
        user.birth_date = None
        user.save()
        self.assertEqual(user.age, None)

    def test_upload_picture(self):
        """Test the uploaded path of pictures
        """
        user = get_user_model().objects.get(pk=1)
        # Create a dummy picture first.
        old_filename = "dummy.png"
        user.picture = old_filename
        user.save()
        # Change user picture
        filename = "my_avatar.png"
        path = get_image_path(user, filename)
        user.picture = filename
        user.save()
        # Path should be differ from filename
        self.assertNotEqual(filename, path)
        # user picture should be changed.
        self.assertNotEqual(user.picture, old_filename)
        # Check if the correct path is returned
        picture_re = re.compile(
            "^%(picture_path)s/[a-f0-9]{40}.png$"
            % {"picture_path": defaults.MANIFEST_PICTURE_PATH}
        )
        self.assertTrue(picture_re.search(path))

    def test_picture_url(self):
        """The user has uploaded it's own picture. This should be returned.
        """
        filename = "fake_image.png"
        user = get_user_model().objects.get(pk=1)
        user.picture = filename
        user.save()
        self.assertEqual(user.picture.url, settings.MEDIA_URL + filename)

    def test_mugshot(self):
        """The user has uploaded it's own picture. This should be returned.
        """
        user = get_user_model().objects.get(pk=1)
        user.picture = self.raw_image_file
        user.save()
        self.assertEqual(user.get_avatar(), user.mugshot.url)

    def test_get_picture_url_without_gravatar(self):
        """Test if the correct picture is returned for the user when
        ``MANIFEST_PICTURE_GRAVATAR`` is set to ``False``.
        """
        user = get_user_model().objects.get(pk=1)
        # This user has no picture, and gravatar is disabled. And to make
        # matters worse, there isn't even a default image.
        with self.defaults(MANIFEST_AVATAR_DEFAULT=None):
            self.assertEqual(user.get_avatar(), None)
        # There is a default image
        # Check that get avatar return a muhgshot url.
        with self.defaults(MANIFEST_AVATAR_DEFAULT="fake_image.png"):
            self.assertEqual(user.get_avatar(), "fake_image.png")

    def test_get_picture_url_with_gravatar(self):
        """Test if the correct picture is returned
        when the user makes use of gravatar.
        """
        template = (
            "http://www.gravatar.com/avatar/%(hash)s?s=%(size)s&d=%(default)s"
        )
        user = get_user_model().objects.get(pk=1)
        gravatar_hash = hashlib.md5(user.email.encode("utf-8")).hexdigest()
        # Test with the default settings
        self.assertEqual(
            user.get_avatar(),
            template
            % {
                "hash": gravatar_hash,
                "size": defaults.MANIFEST_AVATAR_SIZE,
                "default": defaults.MANIFEST_GRAVATAR_DEFAULT,
            },
        )

    def test_get_full_name_or_username(self):
        """Test if the full name or username are returned correcly.
        """
        user = get_user_model().objects.get(pk=1)
        # Profile #1 has a first and last name
        full_name = user.get_full_name_or_username()
        self.assertEqual(full_name, "John Smith")
        # Let's empty out his name, now we should get his username
        user.first_name = ""
        user.last_name = ""
        user.save()

        self.assertEqual(user.get_full_name_or_username(), "john")

    def test_get_short_name_or_username(self):
        """Test if the short name or username are returned correcly.
        """
        user = get_user_model().objects.get(pk=1)
        # Profile #1 has a first and last name
        short_name = user.get_short_name_or_username()
        self.assertEqual(short_name, "John S.")
        # Let's empty out his name, now we should get his username
        user.first_name = ""
        user.last_name = ""
        user.save()
        self.assertEqual(user.get_short_name_or_username(), "john")
