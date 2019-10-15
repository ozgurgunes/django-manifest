# -*- coding: utf-8 -*-
""" Manifest Serializer Tests
"""

from django.contrib.auth import get_user_model

from rest_framework.serializers import ModelSerializer, Serializer

from manifest import serializers
from tests import data_dicts
from tests.base import ManifestTestCase, ManifestUploadTestCase


class SerializerTestCase(ManifestTestCase):
    """Test case for REST serializers.
    """

    user = None
    serializer_class = Serializer
    data_dicts = {"invalid": [], "valid": []}

    def invalid_test(self):
        """An invalid serializer should raise ``ValidationError``.
        """
        for invalid_dict in self.data_dicts["invalid"]:
            if self.user:
                if issubclass(self.serializer_class, ModelSerializer):
                    serializer = self.serializer_class(
                        self.user, data=invalid_dict["data"]
                    )
                else:
                    serializer = self.serializer_class(
                        user=self.user, data=invalid_dict["data"]
                    )
            else:
                serializer = self.serializer_class(data=invalid_dict["data"])

            self.assertFalse(serializer.is_valid())
            self.assertEqual(
                serializer.errors[invalid_dict["error"][0]],
                invalid_dict["error"][1],
            )

    def valid_test(self):
        """A valid serializer should return ``True``.
        """
        for valid_dict in self.data_dicts["valid"]:
            if self.user:
                if issubclass(self.serializer_class, ModelSerializer):
                    serializer = self.serializer_class(
                        self.user, data=valid_dict
                    )
                else:
                    serializer = self.serializer_class(
                        user=self.user, data=valid_dict
                    )
            else:
                serializer = self.serializer_class(data=valid_dict)
            self.assertTrue(serializer.is_valid())


class LoginSerializerTests(SerializerTestCase):
    """Tests for :class:`LoginSerializer
    <manifest.serializers.LoginSerializer>`.
    """

    serializer_class = serializers.LoginSerializer
    data_dicts = data_dicts.LOGIN_SERIALIZER

    def test_invalid_serializer(self):
        self.invalid_test()

    def test_valid_serializer(self):
        self.valid_test()


class RegisterSerializerTests(SerializerTestCase):
    """Tests for :class:`RegisterSerializer
    <manifest.serializers.RegisterSerializer>`.
    """

    serializer_class = serializers.RegisterSerializer
    data_dicts = data_dicts.REGISTER_SERIALIZER

    def test_invalid_serializer(self):
        self.invalid_test()

    def test_valid_serializer(self):
        self.valid_test()


class PasswordResetSerializerTests(SerializerTestCase):
    """Tests for :class:`PasswordResetSerializer
    <manifest.serializers.PasswordResetSerializer>`.
    """

    serializer_class = serializers.PasswordResetSerializer
    data_dicts = data_dicts.PASSWORD_RESET_SERIALIZER

    def test_invalid_serializer(self):
        self.invalid_test()

    def test_valid_serializer(self):
        self.valid_test()


class PasswordChangeSerializerTests(SerializerTestCase):
    """Tests for :class:`PasswordChangeSerializer
    <manifest.serializers.PasswordChangeSerializer>`.
    """

    serializer_class = serializers.PasswordChangeSerializer
    data_dicts = data_dicts.PASSWORD_CHANGE_SERIALIZER

    def setUp(self):
        self.user = get_user_model().objects.get(pk=1)
        super(PasswordChangeSerializerTests, self).setUp()

    def test_invalid_serializer(self):
        self.invalid_test()

    def test_valid_serializer(self):
        self.valid_test()


class EmailChangeSerializerTests(SerializerTestCase):
    """Tests for :class:`EmailChangeSerializer
    <manifest.serializers.EmailChangeSerializer>`.
    """

    serializer_class = serializers.EmailChangeSerializer
    data_dicts = data_dicts.EMAIL_CHANGE_SERIALIZER

    def setUp(self):
        self.user = get_user_model().objects.get(pk=1)
        super(EmailChangeSerializerTests, self).setUp()

    def test_invalid_serializer(self):
        self.invalid_test()

    def test_valid_serializer(self):
        self.valid_test()


class ProfileUpdateSerializerTests(SerializerTestCase):
    """Tests for :class:`ProfileUpdateSerializer
    <manifest.serializers.ProfileUpdateSerializer>`.
    """

    serializer_class = serializers.ProfileUpdateSerializer
    data_dicts = data_dicts.PROFILE_UPDATE_SERIALIZER

    def setUp(self):
        self.user = get_user_model().objects.get(pk=1)
        super(ProfileUpdateSerializerTests, self).setUp()

    def test_invalid_serializer(self):
        self.invalid_test()

    def test_valid_serializer(self):
        self.valid_test()


class RegionUpdateSerializerTests(SerializerTestCase):
    """Tests for :class:`RegionUpdateSerializer
    <manifest.serializers.RegionUpdateSerializer>`.
    """

    serializer_class = serializers.RegionUpdateSerializer
    data_dicts = data_dicts.REGION_UPDATE_SERIALIZER

    def setUp(self):
        self.user = get_user_model().objects.get(pk=1)
        super().setUp()

    def test_invalid_serializer(self):
        self.invalid_test()

    def test_valid_serializer(self):
        self.valid_test()


# pylint: disable=too-many-ancestors
class PictureUploadSerializerTests(SerializerTestCase, ManifestUploadTestCase):
    """Tests for :class:`PictureUploadSerializer
    <manifest.serializers.PictureUploadSerializer>`.
    """

    serializer_class = serializers.PictureUploadSerializer
    data_dicts = None

    def setUp(self):
        self.user = get_user_model().objects.get(pk=1)
        super().setUp()
        self.data_dicts = data_dicts.picture_upload_serializer(self)

    def test_invalid_serializer(self):
        self.invalid_test()

    def test_valid_serializer(self):
        self.valid_test()

    def test_file_size(self):
        with self.upload_limit():
            serializer = self.serializer_class(
                self.user, data=self.data_dicts["invalid_file_size"]["data"]
            )
            serializer.is_valid()
            self.assertEqual(
                serializer.errors[
                    self.data_dicts["invalid_file_size"]["error"][0]
                ],
                self.data_dicts["invalid_file_size"]["error"][1],
            )

    def test_file_type(self):
        serializer = self.serializer_class(
            self.user, self.data_dicts["invalid_file_type"]["data"]
        )
        serializer.is_valid()
        self.assertEqual(
            serializer.errors[
                self.data_dicts["invalid_file_type"]["error"][0]
            ],
            self.data_dicts["invalid_file_type"]["error"][1],
        )

    def test_file_extension(self):
        serializer = self.serializer_class(
            self.user, self.data_dicts["invalid_file_extension"]["data"]
        )
        serializer.is_valid()
        self.assertTrue(
            "File extension “svg” is not allowed."
            in serializer.errors[
                self.data_dicts["invalid_file_extension"]["error"][0]
            ][0]
        )
