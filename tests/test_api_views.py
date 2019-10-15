# -*- coding: utf-8 -*-
""" Manifest API View Tests
"""

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import override_settings
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from tests import data_dicts
from tests.base import (
    TEMPFILE_MEDIA_ROOT,
    ManifestAPITestCase,
    ManifestUploadTestCase,
)


class AuthLoginAPIViewTests(ManifestAPITestCase):
    """Tests for :class:`AuthLoginAPIView
    <manifest.api_views.AuthLoginAPIView>`.
    """

    user_data = ["john", "pass"]
    serializer_data = data_dicts.LOGIN_FORM["valid"][0]

    def test_auth_login_inactive(self):
        """A ``POST`` from an inactive user should raise ``ValidationError``.
        """
        user = get_user_model().objects.get(username=self.user_data[0])
        user.is_active = False
        user.save()
        response = self.client.post(
            reverse("auth_login_api"), data=self.serializer_data
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json["nonFieldErrors"][0],
            _("User account is not activated."),
        )

    def test_auth_login_invalid(self):
        """A ``POST`` with an invalid form should raise ``ValidationError``.
        """
        response = self.client.post(reverse("auth_login_api"), data={})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json["identification"][0],
            _("Please enter your username or email address."),
        )

    def test_auth_login_success(self):
        """A ``POST`` with a valid form should return ``token``.
        """
        response = self.client.post(
            reverse("auth_login_api"), data=self.serializer_data
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual("token" in response.json.keys(), True)


class AuthLogoutTests(ManifestAPITestCase):
    """Tests for :class:`AuthLogoutAPIView
    <manifest.api_views.AuthLogoutAPIView>`.
    """

    def test_auth_logout_post(self):
        """A ``POST`` to the logout view should return ``200``.
        """
        response = self.client.post(reverse("auth_logout_api"))
        self.assertEqual(response.status_code, 200)

    def test_auth_logout_get(self):
        """
        A ``GET`` to the logout view should return ``405`` if
        ``MANIFEST_LOGOUT_ON_GET`` is ``False`` (default).
        """
        with self.defaults(MANIFEST_LOGOUT_ON_GET=False):
            response = self.client.get(reverse("auth_logout_api"))
            self.assertEqual(response.status_code, 405)
        with self.defaults(MANIFEST_LOGOUT_ON_GET=True):
            response = self.client.get(reverse("auth_logout_api"))
            self.assertEqual(response.status_code, 200)


class AuthRegisterAPIViewTests(ManifestAPITestCase):
    """Tests for :class:`AuthRegisterAPIView
    <manifest.api_views.AuthRegisterAPIView>`.
    """

    user_data = ["john", "pass"]
    serializer_data = data_dicts.REGISTER_FORM["valid"][0]

    def test_auth_register_invalid(self):
        """A ``POST`` with an invalid form should raise ``ValidationError``.
        """
        response = self.client.post(reverse("auth_register_api"), data={})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json["email"][0], _("This field is required.")
        )

    def test_auth_register_authenticated(self):
        """A ``POST`` from an authenticated user should return ``403``.
        """
        self.client.login(
            username=self.user_data[0], password=self.user_data[1]
        )
        response = self.client.post(
            reverse("auth_register_api"), data=self.serializer_data
        )
        self.assertEqual(response.status_code, 403)

    def test_auth_register_success(self):
        """A ``POST`` with a valid form should create a new user acount.
        """
        self.client.post(
            reverse("auth_register_api"), data=self.serializer_data
        )
        # Check for new user.
        self.assertEqual(
            get_user_model().objects.filter(username="alice").count(), 1
        )


class AuthActivateAPIViewTests(ManifestAPITestCase):
    """Tests for :class:`AuthActivateAPIView
    <manifest.api_views.AuthActivateAPIView>`.
    """

    serializer_data = data_dicts.REGISTER_FORM["valid"][0]

    def test_activate_success(self):
        """
        A ``POST`` with a valid token should activate the user account.
        """
        self.client.post(
            reverse("auth_register_api"), data=self.serializer_data
        )
        user = get_user_model().objects.get(email="alice@example.com")
        response = self.client.post(
            reverse("auth_activate_api"),
            data={"username": user.username, "token": user.activation_key},
        )
        self.assertEqual(response.status_code, 200)
        user = get_user_model().objects.get(username="alice")
        self.assertTrue(user.is_active)

    def test_activate_invalid(self):
        """A ``POST`` with an invalid token should raise ``ValidationError``.
        """
        response = self.client.post(
            reverse("auth_activate_api"),
            data={"username": "alice", "token": "fake"},
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json["nonFieldErrors"][0], _("Token validation failed.")
        )


class PasswordResetAPIViewTests(ManifestAPITestCase):
    """Tests for :class:`PasswordResetAPIView
    <manifest.api_views.PasswordResetAPIView>`.
    """

    def test_password_reset_success(self):
        """A ``POST`` with a valid email should send password reset mail.
        """
        response = self.client.post(
            reverse("password_reset_api"), data={"email": "john@example.com"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)

    def test_password_reset_invalid(self):
        """A ``POST`` with an invalid email should raise ``ValidationError``.
        """
        response = self.client.post(
            reverse("password_reset_api"), data={"email": "dummy"}
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json["email"][0], _("Enter a valid email address.")
        )
        self.assertEqual(len(mail.outbox), 0)

    def test_password_reset_fail(self):
        """A ``POST`` with a non-existed email should fail silently.
        """
        response = self.client.post(
            reverse("password_reset_api"), data={"email": "john@dummy.com"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)


class PasswordResetVerifyAPIViewTests(ManifestAPITestCase):
    """Tests for :class:`PasswordResetVerifyAPIView
    <manifest.api_views.PasswordResetVerifyAPIView>`.
    """

    def test_password_reset_verify_success(self):
        """A ``POST`` with a valid token should return success.
        """
        response = self.client.post(
            reverse("password_reset_api"), data={"email": "john@example.com"}
        )
        uid = response.context["uid"]
        token = response.context["token"]
        response = self.client.post(
            reverse("password_reset_verify_api"),
            data={"uid": uid, "token": token},
        )
        self.assertEqual(response.status_code, 200)

    def test_password_reset_verify_invalid(self):
        """A ``POST`` with an invalid token should raise ``ValidationError``.
        """
        response = self.client.post(
            reverse("password_reset_api"), data={"email": "john@example.com"}
        )
        uid = response.context["uid"]
        token = response.context["token"]
        response = self.client.post(
            reverse("password_reset_verify_api"),
            data={"uid": "uid", "token": token},
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json["uid"][0], _("Invalid uid."))
        response = self.client.post(
            reverse("password_reset_verify_api"),
            data={"uid": uid, "token": "token"},
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json["token"][0], _("Invalid token."))


class PasswordResetConfirmAPIViewTests(ManifestAPITestCase):
    """Tests for :class:`PasswordResetConfirmAPIView
    <manifest.api_views.PasswordResetConfirmAPIView>`.
    """

    def test_password_reset_confirm_success(self):
        """A ``POST`` with a valid token and form should return success.
        """
        response = self.client.post(
            reverse("password_reset_api"), data={"email": "john@example.com"}
        )
        uid = response.context["uid"]
        token = response.context["token"]
        response = self.client.post(
            reverse("password_reset_confirm_api"),
            data={
                "uid": uid,
                "token": token,
                "new_password1": "newpass",
                "new_password2": "newpass",
            },
        )
        self.assertEqual(response.status_code, 200)

    def test_password_reset_confirm_invalid_uid(self):
        """A ``POST`` with an invalid uid should raise ``ValidationError``.
        """
        response = self.client.post(
            reverse("password_reset_api"), data={"email": "john@example.com"}
        )
        response = self.client.post(
            reverse("password_reset_confirm_api"),
            data={
                "uid": "uid",
                "token": "token",
                "new_password1": "newpass",
                "new_password2": "newpass",
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json["uid"][0], _("Invalid uid."))

    def test_password_reset_confirm_invalid_token(self):
        """A ``POST`` with an invalid token should raise ``ValidationError``.
        """
        response = self.client.post(
            reverse("password_reset_api"), data={"email": "john@example.com"}
        )
        uid = response.context["uid"]
        response = self.client.post(
            reverse("password_reset_confirm_api"),
            data={
                "uid": uid,
                "token": "token",
                "new_password1": "newpass",
                "new_password2": "newpass",
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json["token"][0], _("Invalid token."))

    def test_password_reset_confirm_invalid_password(self):
        """A ``POST`` with an invalid form should raise ``ValidationError``.
        """
        response = self.client.post(
            reverse("password_reset_api"), data={"email": "john@example.com"}
        )
        uid = response.context["uid"]
        token = response.context["token"]
        response = self.client.post(
            reverse("password_reset_confirm_api"),
            data={
                "uid": uid,
                "token": token,
                "new_password1": "newpass1",
                "new_password2": "newpass2",
            },
        )
        self.assertEqual(
            response.json["newPassword2"][0],
            _("The two password fields didn’t match."),
        )


class AuthProfileAPIViewTests(ManifestAPITestCase):
    """Tests for :class:`ProfileUpdateAPIView
    <manifest.api_views.ProfileUpdateAPIView>`.
    """

    user_data = ["john", "pass"]
    serializer_data = data_dicts.PROFILE_UPDATE_SERIALIZER["valid"][0]

    def test_auth_profile_get(self):
        """A ``GET`` should return profile information.
        """
        self.client.login(
            username=self.user_data[0], password=self.user_data[1]
        )
        response = self.client.get(reverse("auth_profile_api"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue("avatar" in response.json.keys())

    def test_profile_update_invalid(self):
        """A ``POST`` with an ivalid form should raise ``ValidationError``.
        """
        self.client.login(
            username=self.user_data[0], password=self.user_data[1]
        )
        response = self.client.put(reverse("profile_update_api"), data={})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json["birthDate"][0], _("This field is required.")
        )

    def test_profile_update_success(self):
        """A ``POST`` with a valid form should update user info.
        """
        self.client.login(
            username=self.user_data[0], password=self.user_data[1]
        )
        response = self.client.put(
            reverse("profile_update_api"), data=self.serializer_data
        )
        self.assertEqual(response.status_code, 200)

    def test_region_update_invalid(self):
        """A ``POST`` with an ivalid form should raise ``ValidationError``.
        """
        self.client.login(
            username=self.user_data[0], password=self.user_data[1]
        )
        response = self.client.put(reverse("region_update_api"), data={})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json["timezone"][0], _("This field is required.")
        )

    def test_region_update_success(self):
        """A ``POST`` with a valid form should update user info.
        """
        self.client.login(
            username=self.user_data[0], password=self.user_data[1]
        )
        response = self.client.put(
            reverse("region_update_api"),
            data=data_dicts.REGION_UPDATE_SERIALIZER["valid"][0],
        )
        self.assertEqual(response.status_code, 200)


class ProfileOptionsAPIViewTests(ManifestAPITestCase):
    """Tests for :class:`ProfileOptionsAPIView
    <manifest.api_views.ProfileOptionsAPIView>`.
    """

    user_data = ["john", "pass"]

    def test_profile_options_dict(self):
        """A ``GET`` should return a dictionary containing ``gender``,
        ``timezone`` and ``locale`` keys.
        """
        self.client.login(
            username=self.user_data[0], password=self.user_data[1]
        )
        response = self.client.get(reverse("profile_options_api"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue("gender" in response.json.keys())
        self.assertTrue("timezone" in response.json.keys())
        self.assertTrue("locale" in response.json.keys())


# pylint: disable=too-many-ancestors
@override_settings(MEDIA_ROOT=TEMPFILE_MEDIA_ROOT)
class PictureUploadAPIViewTests(ManifestAPITestCase, ManifestUploadTestCase):
    """Tests for :class:`PictureUploadAPIView
    <manifest.api_views.PictureUploadAPIView>`.
    """

    user_data = ["john", "pass"]

    def test_picture_upload_success(self):
        """A ``POST`` with a valid serializer should update profile picture.
        """
        # Authenticate user
        self.client.login(
            username=self.user_data[0], password=self.user_data[1]
        )
        # Post a valid serializer.
        response = self.client.post(
            reverse("picture_upload_api"), data={"picture": self.image_file}
        )
        self.assertEqual(response.status_code, 200)

    def test_picture_upload_invalid(self):
        """A ``POST`` with an invalid serializer should
        raise ``ValidationError``.
        """
        self.client.login(
            username=self.user_data[0], password=self.user_data[1]
        )
        response = self.client.post(reverse("picture_upload_api"), data={})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json["picture"][0], _("No file was submitted.")
        )

    def test_picture_upload_file_size(self):
        """A ``POST`` with an invalid picture should raise ``ValidationError``.
        """
        self.client.login(
            username=self.user_data[0], password=self.user_data[1]
        )
        with self.upload_limit():
            response = self.client.post(
                reverse("picture_upload_api"),
                data={"picture": self.image_file},
            )
            self.assertEqual(response.status_code, 400)
            self.assertEqual(
                response.json["picture"][0], _("Image size is too big.")
            )


class EmailChangeAPIViewTests(ManifestAPITestCase):
    """Tests for :class:`EmailChangeAPIView
    <manifest.api_views.EmailChangeAPIView>`.
    """

    user_data = ["john", "pass"]
    serializer_data = data_dicts.EMAIL_CHANGE_FORM["valid"][0]

    def test_email_change_unauthorized(self):
        """A ``POST`` from an unauthorized user should return ``401``.
        """
        response = self.client.post(
            reverse("email_change_api"), data=self.serializer_data
        )
        self.assertEqual(response.status_code, 401)

    def test_email_change_success(self):
        """A ``POST`` with a valid form should save new email.
        """
        self.client.login(
            username=self.user_data[0], password=self.user_data[1]
        )
        response = self.client.post(
            reverse("email_change_api"), data=self.serializer_data
        )
        self.assertEqual(response.status_code, 200)

    def test_email_change_invalid(self):
        """A ``POST`` with an invalid form should raise ``ValidationError``.
        """
        self.client.login(
            username=self.user_data[0], password=self.user_data[1]
        )
        response = self.client.post(reverse("email_change_api"), data={})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json["email"][0], _("This field is required.")
        )


class EmailChangeConfirmAPIViewTests(ManifestAPITestCase):
    """Tests for :class:`EmailChangeConfirmAPIView
    <manifest.api_views.EmailChangeConfirmAPIView>`.
    """

    user_data = ["john", "pass"]

    def test_email_change_confirm_success(self):
        """A ``POST`` with a valid token should change the email.
        """
        # First, try to change an email.
        self.client.login(
            username=self.user_data[0], password=self.user_data[1]
        )
        user = get_user_model().objects.get(username=self.user_data[0])
        user.change_email("john.smith@example.com")
        self.assertEqual(user.email_unconfirmed, "john.smith@example.com")
        self.assertNotEqual(user.email, "john.smith@example.com")
        response = self.client.post(
            reverse("email_change_confirm_api"),
            data={
                "username": user.username,
                "token": user.email_confirmation_key,
            },
        )
        self.assertEqual(response.status_code, 200)
        user = get_user_model().objects.get(username=self.user_data[0])
        # Check for email changed.
        self.assertEqual(user.email, "john.smith@example.com")

    def test_email_change_confirm_invalid(self):
        """A ``POST`` with an invalid token should raise ``ValidationError``.
        """
        response = self.client.post(
            reverse("email_change_confirm_api"),
            data={"username": "john", "token": "WRONG"},
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json["nonFieldErrors"][0], _("Token validation failed.")
        )


class PasswordChangeAPIViewTests(ManifestAPITestCase):
    """Tests for :class:`PasswordChangeAPIView
    <manifest.api_views.PasswordChangeAPIView>`.
    """

    user_data = ["john", "pass"]
    serializer_data = data_dicts.PASSWORD_CHANGE_SERIALIZER["valid"][0]

    def test_password_change_invalid(self):
        """A ``PATCH`` with an invalid form should raise ``ValidationError``.
        """
        self.client.login(
            username=self.user_data[0], password=self.user_data[1]
        )
        response = self.client.patch(reverse("password_change_api"))
        self.assertEqual(response.status_code, 400)

    def test_password_change_success(self):
        """A ``PATCH`` with a valid form should change password.
        """
        self.client.login(
            username=self.user_data[0], password=self.user_data[1]
        )
        self.client.patch(
            reverse("password_change_api"), data=self.serializer_data
        )
        # Check that the new password is set.
        john = get_user_model().objects.get(username="john")
        self.assertTrue(
            john.check_password(self.serializer_data["new_password1"])
        )


class UserListAPIViewTests(ManifestAPITestCase):
    """Tests for :class:`UserListAPIView
    <manifest.api_views.UserListAPIView>`.
    """

    user_data = ["jane", "pass"]

    def test_user_list_view(self):
        """A ``GET`` to the view should return list of users if
        ``MANIFEST_DISABLE_PROFILE_LIST`` setting is ``False`` (default).
        """
        # A profile list should be shown.
        self.client.login(
            username=self.user_data[0], password=self.user_data[1]
        )
        with self.defaults(MANIFEST_DISABLE_PROFILE_LIST=False):
            response = self.client.get(reverse("user_list_api"))
            self.assertEqual(response.status_code, 200)

    def test_user_list_disabled(self):
        """A ``GET`` to the view should return ``404`` if
        ``MANIFEST_DISABLE_PROFILE_LIST`` setting is ``True``.
        """
        self.client.login(
            username=self.user_data[0], password=self.user_data[1]
        )
        with self.defaults(MANIFEST_DISABLE_PROFILE_LIST=True):
            response = self.client.get(reverse("user_list_api"))
            self.assertEqual(response.status_code, 404)


class UserDetailAPIViewTests(ManifestAPITestCase):
    """Tests for :class:`UserDetailAPIView
    <manifest.api_views.UserDetail>APIView`.
    """

    user_data = ["john", "pass"]

    def test_user_detail_view(self):
        """A ``GET`` to the view should return user info if
        ``MANIFEST_DISABLE_PROFILE_LIST`` setting is ``False`` (default).
        """
        with self.defaults(MANIFEST_DISABLE_PROFILE_LIST=False):
            response = self.client.get(
                reverse("user_detail_api", kwargs={"username": "john"})
            )
            self.assertEqual(response.status_code, 200)

    def test_user_detail_disabled(self):
        """A ``GET`` to the view should return ``404`` if
        ``MANIFEST_DISABLE_PROFILE_LIST`` setting is ``True``.
        """
        with self.defaults(MANIFEST_DISABLE_PROFILE_LIST=True):
            response = self.client.get(
                reverse("user_detail_api", kwargs={"username": "john"})
            )
            self.assertEqual(response.status_code, 404)
