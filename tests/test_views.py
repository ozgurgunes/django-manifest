# -*- coding: utf-8 -*-
""" Manifest View Tests
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    PasswordChangeForm,
    PasswordResetForm,
    SetPasswordForm,
)
from django.core import mail
from django.test import override_settings
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from manifest import defaults, forms
from tests import data_dicts
from tests.base import (
    TEMPFILE_MEDIA_ROOT,
    ManifestTestCase,
    ManifestUploadTestCase,
)
from tests.urls import TEST_REGISTER_FORM_CLASS, TEST_SUCCESS_URL


class AuthLoginViewTests(ManifestTestCase):
    """Tests for :class:`AuthLoginView <manifest.views.AuthLoginView>`.
    """

    user_data = ["john", "pass"]
    form_data = data_dicts.LOGIN_FORM["valid"][0]

    def test_auth_login_view(self):
        """A ``GET`` to the view should render the correct form.
        """
        response = self.client.get(reverse("auth_login"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "manifest/auth_login.html")

    def test_auth_login_invalid(self):
        """A ``POST`` with an invalid form should render
        the template with ``ValidationError``.
        """
        response = self.client.post(reverse("auth_login"), data={})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "manifest/auth_login.html")
        self.assertEqual(
            response.context["form"].errors["identification"][0],
            _("Please enter your username or email address."),
        )

    def test_auth_login_inactive(self):
        """A ``POST`` with an inactive user should
        redirect to ``auth_disabled``.
        """
        user = get_user_model().objects.get(username=self.user_data[0])
        user.is_active = False
        user.save()
        response = self.client.post(reverse("auth_login"), data=self.form_data)
        self.assertRedirects(response, reverse("auth_disabled"))

    def test_auth_login_success(self):
        """A ``POST`` with a valid form should redirect to
        ``profile_settings`` if no ``next`` is supplied.
        Else, it should redirect to ``next``.
        """
        response = self.client.post(reverse("auth_login"), data=self.form_data)
        self.assertRedirects(response, defaults.MANIFEST_LOGIN_REDIRECT_URL)
        # Redirect to ``next``.
        response = self.client.post(
            reverse("auth_login"), data={**self.form_data, "next": "/test/"}
        )
        self.assertRedirects(response, "/test/")

    def test_auth_login_success_url(self):
        """A ``POST`` with a valid form should redirect to ``success_url``.
        """
        response = self.client.post(
            reverse("test_auth_login_success_url"), data=self.form_data
        )
        self.assertRedirects(response, TEST_SUCCESS_URL)


class AuthLogoutViewTests(ManifestTestCase):
    """Tests for :class:`AuthLogoutView <manifest.views.AuthLogoutView>`.
    """

    def test_auth_logout_view(self):
        """A ``GET`` to the view should render the correct template.
        """
        response = self.client.get(reverse("auth_logout"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "manifest/auth_logout.html")


class AuthRegisterViewTests(ManifestTestCase):
    """Tests for :class:`AuthRegisterView <manifest.views.AuthRegisterView>`.
    """

    user_data = ["john", "pass"]
    form_data = data_dicts.REGISTER_FORM["valid"][0]

    def test_auth_register_view(self):
        """A ``GET`` to the view should render the correct form.
        """
        response = self.client.get(reverse("auth_register"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "manifest/auth_register.html")
        self.assertTrue(
            isinstance(response.context["form"], forms.RegisterForm)
        )

    def test_auth_register_invalid(self):
        """A ``POST`` with an invalid form should render
        the template with ``ValidationError``.
        """
        response = self.client.post(reverse("auth_register"), data={})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "manifest/auth_register.html")
        self.assertEqual(
            response.context["form"].errors["email"][0],
            _("This field is required."),
        )

    def test_auth_register_authenticated(self):
        """Any ``REQUEST`` from an authenticated user should
        redirect to ``profile_settings``.
        """
        # Authenticate user
        self.assertTrue(
            self.client.login(
                username=self.user_data[0], password=self.user_data[1]
            )
        )
        # A ``GET`` from and authenticated user.
        response = self.client.get(reverse("auth_register"))
        self.assertRedirects(response, reverse("profile_settings"))
        # A ``POST`` from and authenticated user.
        response = self.client.post(
            reverse("auth_register"), data=self.form_data
        )
        self.assertRedirects(response, reverse("profile_settings"))

    def test_auth_register_success(self):
        """A ``POST`` with a valid form should create a new user acount
        and redirect to ``auth_register_complete``.
        """
        response = self.client.post(
            reverse("auth_register"), data=self.form_data
        )
        # Check for redirect.
        self.assertRedirects(response, reverse("auth_register_complete"))
        # Check for new user.
        self.assertEqual(
            get_user_model().objects.filter(username="alice").count(), 1
        )

    def test_auth_register_success_url(self):
        """A ``POST`` with a valid form should redirect to ``success_url``.
        """
        response = self.client.post(
            reverse("test_auth_register_success_url"), data=self.form_data
        )
        self.assertRedirects(response, TEST_SUCCESS_URL)

    def test_auth_register_form_class(self):
        """A ``POST`` with a valid form should create a new user acount
        and redirect to ``success_url``.
        """
        response = self.client.get(reverse("test_auth_register_form_class"))
        self.assertTrue(
            isinstance(response.context["form"], TEST_REGISTER_FORM_CLASS)
        )


class AuthActivateViewTests(ManifestTestCase):
    """Tests for :class:`AuthActivateView <manifest.views.AuthActivateView>`.
    """

    user_data = ["alice", "wonderland"]
    form_data = data_dicts.REGISTER_FORM["valid"][0]

    def test_auth_activation_success(self):
        """A ``GET`` with a valid token should acticate the user
        and redirect to ``profile_settings``.
        """
        self.client.post(reverse("auth_register"), data=self.form_data)
        user = get_user_model().objects.get(username=self.user_data[0])
        response = self.client.get(
            reverse(
                "auth_activate",
                kwargs={
                    "username": user.username,
                    "token": user.activation_key,
                },
            )
        )
        self.assertRedirects(response, reverse("profile_settings"))
        user = get_user_model().objects.get(username=self.user_data[0])
        self.assertTrue(user.is_active)

    def test_auth_activation_invalid(self):
        """A ``GET`` with an invalid token should render the correct template.
        """
        response = self.client.get(
            reverse(
                "auth_activate", kwargs={"username": "alice", "token": "fake"}
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "manifest/auth_activate.html")

    def test_auth_activate_success_url(self):
        """A ``GET`` with a valid token should redirect to ``success_url``.
        """
        response = self.client.post(
            reverse("auth_register"), data=self.form_data
        )
        user = get_user_model().objects.get(username=self.user_data[0])
        response = self.client.get(
            reverse(
                "test_auth_activate_success_url",
                kwargs={
                    "username": user.username,
                    "token": user.activation_key,
                },
            )
        )
        self.assertRedirects(response, TEST_SUCCESS_URL)


class PasswordResetTests(ManifestTestCase):
    """Tests for :class:`PasswordResetView
    <manifest.views.PasswordResetView>`.
    """

    def test_password_reset_view(self):
        """A ``GET`` to the view should render the correct form.
        """
        response = self.client.get(reverse("password_reset"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "manifest/password_reset_form.html")
        self.assertTrue(
            isinstance(response.context["form"], PasswordResetForm)
        )

    def test_password_reset_success(self):
        """A ``POST`` with a valid email should send password reset mail.
        """
        response = self.client.post(
            reverse("password_reset"), data={"email": "john@example.com"}
        )
        self.assertRedirects(response, reverse("password_reset_done"))
        self.assertEqual(len(mail.outbox), 1)

    def test_password_reset_invalid(self):
        """A ``POST`` with an invalid email should render
        the template with ``ValidationError``.
        """
        response = self.client.post(
            reverse("password_reset"), data={"email": "dummy"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "manifest/password_reset_form.html")
        self.assertEqual(
            response.context["form"].errors["email"][0],
            _("Enter a valid email address."),
        )

    def test_password_reset_fail(self):
        """A ``POST`` with a non-existed email should fail silently.
        """
        response = self.client.post(
            reverse("password_reset"), data={"email": "john@dummy.com"}
        )
        self.assertRedirects(response, reverse("password_reset_done"))
        self.assertEqual(len(mail.outbox), 0)


class PasswordResetConfirmViewTests(ManifestTestCase):
    """Tests for :class:`PasswordResetConfirmView
    <manifest.views.PasswordResetConfirmView>`.
    """

    def test_password_reset_confirm_success(self):
        """A ``POST`` with a valid token should return success.
        """
        response = self.client.post(
            reverse("password_reset"), data={"email": "john@example.com"}
        )
        uid = response.context["uid"]
        token = response.context["token"]
        response = self.client.post(
            reverse(
                "password_reset_confirm",
                kwargs={"uidb64": uid, "token": token},
            )
        )
        self.assertEqual(response.status_code, 302)
        response = self.client.get(
            reverse(
                "password_reset_confirm",
                kwargs={"uidb64": uid, "token": "set-password"},
            )
        )
        self.assertTrue(isinstance(response.context["form"], SetPasswordForm))
        response = self.client.post(
            reverse(
                "password_reset_confirm",
                kwargs={"uidb64": uid, "token": "set-password"},
            ),
            data={
                "old_password": "pass",
                "new_password1": "new_pass",
                "new_password2": "new_pass",
            },
        )
        self.assertRedirects(response, reverse("password_reset_complete"))

    def test_password_reset_confirm_invalid(self):
        """A ``POST`` with an invalid token should render
        the template with ``ValidationError``.
        """
        response = self.client.post(
            reverse("password_reset"), data={"email": "john@example.com"}
        )
        uid = response.context["uid"]
        token = response.context["token"]

        response = self.client.post(
            reverse(
                "password_reset_confirm",
                kwargs={"uidb64": "uidb64", "token": token},
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context.get("form", None))
        self.assertContains(response, "Something went wrong!")

        response = self.client.post(
            reverse(
                "password_reset_confirm",
                kwargs={"uidb64": uid, "token": "token"},
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context.get("form", None))
        self.assertContains(response, "Something went wrong!")


class AuthProfileViewTests(ManifestTestCase):
    """Tests for :class:`AuthProfileView <manifest.views.AuthProfileView>`.
    """

    user_data = ["john", "pass"]

    def test_auth_profile_view(self):
        """A ``GET`` to the view should render the correct template.
        """
        self.client.login(
            username=self.user_data[0], password=self.user_data[1]
        )
        response = self.client.get(reverse("user_profile"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "manifest/user_detail.html")

    def test_profile_settings_view(self):
        """A ``GET`` to the view should render the correct template.
        """
        self.client.login(
            username=self.user_data[0], password=self.user_data[1]
        )
        response = self.client.get(reverse("profile_settings"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "manifest/profile_settings.html")


class ProfileUpdateViewTests(ManifestTestCase):
    """Tests for :class:`ProfileUpdateView
    <manifest.views.ProfileUpdateView>`.
    """

    user_data = ["john", "pass"]
    form_data = data_dicts.PROFILE_UPDATE_FORM["valid"][0]

    def test_profile_update_view(self):
        """A ``GET`` to the view should render the correct template.
        """
        self.client.login(
            username=self.user_data[0], password=self.user_data[1]
        )
        response = self.client.get(reverse("profile_update"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "manifest/profile_update.html")
        self.assertTrue(response.context["form"], forms.ProfileUpdateForm)

    def test_profile_update_success(self):
        """A ``POST`` with a valid form should save data
        and redirect to ``profile_settings``.
        """
        self.client.login(
            username=self.user_data[0], password=self.user_data[1]
        )
        response = self.client.post(
            reverse("profile_update"), data=self.form_data
        )
        # Check for redirect.
        self.assertRedirects(response, reverse("profile_settings"))
        # Check for saved data.
        user = get_user_model().objects.get(username=self.user_data[0])
        self.assertEqual(user.gender, "M")

    def test_profile_update_invalid(self):
        """A ``POST`` with an invalid form should render
        the template with ``ValidationError``.
        """
        self.client.login(
            username=self.user_data[0], password=self.user_data[1]
        )
        response = self.client.post(reverse("profile_update"), data={})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "manifest/profile_update.html")
        self.assertEqual(
            response.context["form"].errors["first_name"][0],
            _("This field is required."),
        )

    def test_profile_update_success_url(self):
        """A ``POST`` with a valid form should redirect to ``success_url``.
        """
        self.client.login(
            username=self.user_data[0], password=self.user_data[1]
        )
        response = self.client.post(
            reverse("test_profile_update_success_url"), data=self.form_data
        )
        self.assertRedirects(response, TEST_SUCCESS_URL)

    def test_region_update_view(self):
        """A ``GET`` to the view should render the correct template.
        """
        self.client.login(
            username=self.user_data[0], password=self.user_data[1]
        )
        response = self.client.get(reverse("region_update"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "manifest/region_update.html")
        self.assertTrue(response.context["form"], forms.RegionUpdateForm)

    def test_region_update_success(self):
        """A ``POST`` with a valid form should save data
        and redirect to ``profile_settings``.
        """
        self.client.login(
            username=self.user_data[0], password=self.user_data[1]
        )
        response = self.client.post(
            reverse("region_update"),
            data=data_dicts.REGION_UPDATE_FORM["valid"][0],
        )
        # Check for redirect.
        self.assertRedirects(response, reverse("profile_settings"))
        # Check for saved data.
        user = get_user_model().objects.get(username=self.user_data[0])
        self.assertEqual(user.timezone, "Europe/Istanbul")

    def test_region_update_invalid(self):
        """A ``POST`` with an invalid form should render
        the template with ``ValidationError``.
        """
        self.client.login(
            username=self.user_data[0], password=self.user_data[1]
        )
        response = self.client.post(reverse("region_update"), data={})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "manifest/region_update.html")
        self.assertEqual(
            response.context["form"].errors["timezone"][0],
            _("This field is required."),
        )


@override_settings(MEDIA_ROOT=TEMPFILE_MEDIA_ROOT)
class PictureUploadViewTests(ManifestUploadTestCase):
    """Tests for :class:`PictureUploadView <manifest.views.PictureUploadView>`.
    """

    user_data = ["john", "pass"]

    def test_picture_upload_view(self):
        """A ``GET`` to the view should render the correct template.
        """
        response = self.client.get(reverse("picture_upload"))
        # Anonymous user should not be able to view the profile pages.
        self.assertEqual(response.status_code, 302)
        # Authenticate user.
        self.client.login(
            username=self.user_data[0], password=self.user_data[1]
        )
        response = self.client.get(reverse("picture_upload"))
        self.assertEqual(response.status_code, 200)
        # Check that the correct form is used.
        self.assertTrue(
            isinstance(response.context["form"], forms.PictureUploadForm)
        )
        self.assertTemplateUsed(response, "manifest/picture_upload.html")

    def test_picture_upload_success(self):
        """A ``POST`` with a valid form should update profile picture.
        """
        self.client.login(
            username=self.user_data[0], password=self.user_data[1]
        )
        # Post a valid form.
        response = self.client.post(
            reverse("picture_upload"), data={"picture": self.image_file}
        )
        self.assertRedirects(response, reverse("profile_settings"))

    def test_picture_upload_invalid(self):
        """A ``POST`` with an invalid form should render
        the template with ``ValidationError``.
        """
        self.client.login(
            username=self.user_data[0], password=self.user_data[1]
        )
        response = self.client.post(reverse("picture_upload"), data={})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["form"].errors["picture"][0],
            _("This field is required."),
        )

    def test_picture_clear(self):
        """A ``POST`` with a ``picture-clear`` should
        delete existing profile picture.
        """
        self.client.login(
            username=self.user_data[0], password=self.user_data[1]
        )
        self.client.post(
            reverse("picture_upload"), data={"picture": self.image_file}
        )
        user = get_user_model().objects.get(username=self.user_data[0])
        # Check for a profile picture exists.
        self.assertTrue(user.picture)
        response = self.client.post(
            reverse("picture_upload"), data={"picture-clear": 1}
        )
        self.assertRedirects(response, reverse("profile_settings"))
        user = get_user_model().objects.get(username=self.user_data[0])
        # Check for profile picture deleted.
        self.assertFalse(user.picture)


class EmailChangeViewTests(ManifestTestCase):
    """Tests for :class:`EmailChangeView <manifest.views.EmailChangeView>`.
    """

    user_data = ["john", "pass"]
    form_data = data_dicts.EMAIL_CHANGE_FORM["valid"][0]

    def test_email_change_view(self):
        """A ``GET`` to the view should render the correct template.
        """
        response = self.client.get(reverse("email_change"))
        # Anonymous user should not be able to view the profile pages.
        self.assertEqual(response.status_code, 302)
        # Authenticate user.
        self.client.login(
            username=self.user_data[0], password=self.user_data[1]
        )
        response = self.client.get(reverse("email_change"))
        self.assertEqual(response.status_code, 200)
        # Check that the correct form is used.
        self.assertTrue(
            isinstance(response.context["form"], forms.EmailChangeForm)
        )
        self.assertTemplateUsed(response, "manifest/email_change.html")

    def test_email_change_success(self):
        """A ``POST`` with a valid form should save new email
        and redirect to ``email_change_done``.
        """
        # Login
        self.client.login(
            username=self.user_data[0], password=self.user_data[1]
        )
        response = self.client.post(
            reverse("email_change"), data=self.form_data
        )
        self.assertRedirects(response, reverse("email_change_done"))

    def test_email_change_invalid(self):
        """A ``POST`` with an invalid form should render
        the template with ``ValidationError``.
        """
        self.client.login(
            username=self.user_data[0], password=self.user_data[1]
        )
        response = self.client.post(reverse("email_change"), data={})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["form"].errors["email"][0],
            _("This field is required."),
        )

    def test_email_change_success_url(self):
        """A ``POST`` with a valid form should redirect to ``success_url``.
        """
        # Login
        self.client.login(
            username=self.user_data[0], password=self.user_data[1]
        )
        response = self.client.post(
            reverse("test_email_change_success_url"), data=self.form_data
        )
        self.assertRedirects(response, TEST_SUCCESS_URL)


class EmailChangeConfirmViewTests(ManifestTestCase):
    """Tests for :class:`EmailChangeConfirmView
    <manifest.views.EmailChangeConfirmView>`.
    """

    user_data = ["john", "pass"]

    def test_valid_confirmation(self):
        """A ``GET`` with a valid token should change the email
        and redirect to ``email_change_complete``.
        """
        user = get_user_model().objects.get(username=self.user_data[0])
        user.change_email("john.smith@example.com")
        self.assertEqual(user.email_unconfirmed, "john.smith@example.com")
        self.assertNotEqual(user.email, "john.smith@example.com")
        response = self.client.get(
            reverse(
                "email_change_confirm",
                kwargs={
                    "username": user.username,
                    "token": user.email_confirmation_key,
                },
            )
        )
        self.assertRedirects(response, reverse("email_change_complete"))
        user = get_user_model().objects.get(username=self.user_data[0])
        # Check for email changed.
        self.assertEqual(user.email, "john.smith@example.com")

    def test_invalid_confirmation(self):
        """A ``GET`` with an invalid token should render
        the correct template with ``Error``.
        """
        response = self.client.get(
            reverse(
                "email_change_confirm",
                kwargs={"username": "john", "token": "WRONG"},
            )
        )
        self.assertTemplateUsed(response, "manifest/email_change_confirm.html")

    def test_email_change_confirm_success_url(self):
        """A ``POST`` with a valid form should redirect to ``success_url``.
        """
        user = get_user_model().objects.get(username=self.user_data[0])
        user.change_email("john.smith@example.com")
        response = self.client.get(
            reverse(
                "test_email_change_confirm_success_url",
                kwargs={
                    "username": user.username,
                    "token": user.email_confirmation_key,
                },
            )
        )
        self.assertRedirects(response, TEST_SUCCESS_URL)


class PasswordChangeViewTests(ManifestTestCase):
    """Tests for :class:`PasswordChangeView
    <manifest.views.PasswordChangeView>`.
    """

    user_data = ["john", "pass"]
    form_data = data_dicts.PASSWORD_CHANGE_FORM["valid"][0]

    def test_password_change_view(self):
        """A ``GET`` to the view should render the correct form.
        """
        self.client.login(
            username=self.user_data[0], password=self.user_data[1]
        )
        response = self.client.get(reverse("password_change"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "manifest/password_change.html")
        self.assertTrue(response.context["form"], PasswordChangeForm)

    def test_password_change_success(self):
        """A ``POST`` with a valid form should change user password
        and redirect to ``password_change_done``.
        """
        self.client.login(
            username=self.user_data[0], password=self.user_data[1]
        )
        response = self.client.post(
            reverse("password_change"), data=self.form_data
        )
        self.assertRedirects(response, reverse("password_change_done"))
        # Check that the new password is set.
        john = get_user_model().objects.get(username=self.user_data[0])
        self.assertTrue(john.check_password(self.form_data["new_password1"]))

    def test_password_change_invalid(self):
        """A ``POST`` with an invalid form should render
        the template with ``ValidationError``.
        """
        self.client.login(
            username=self.user_data[0], password=self.user_data[1]
        )
        response = self.client.post(
            reverse("password_change"),
            data={
                "new_password1": "newpass1",
                "new_password2": "newpass2",
                "old_password": "pass",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["form"].errors["new_password2"][0],
            _("The two password fields didn’t match."),
        )

    def test_password_change_success_url(self):
        """A ``POST`` with a valid form should redirect to ``success_url``.
        """
        self.client.login(
            username=self.user_data[0], password=self.user_data[1]
        )
        response = self.client.post(
            reverse("test_password_change_success_url"), data=self.form_data
        )
        self.assertRedirects(response, TEST_SUCCESS_URL)


class UserListViewTests(ManifestTestCase):
    """Tests for :class:`UserListView <manifest.views.UserListView>`.
    """

    def test_user_list_view(self):
        """A ``GET`` to the view should return list of users if
        ``MANIFEST_DISABLE_PROFILE_LIST`` setting is ``False`` (default).
        """
        with self.defaults(MANIFEST_DISABLE_PROFILE_LIST=False):
            response = self.client.get(reverse("user_list"))
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, "manifest/user_list.html")
            response = self.client.get(
                reverse("user_list_paginated", kwargs={"page": 1})
            )
            self.assertEqual(response.status_code, 200)
            response = self.client.get(
                reverse("user_list_paginated", kwargs={"page": 2})
            )
            self.assertEqual(response.status_code, 200)

    def test_user_list_disabled(self):
        """A ``GET`` to the view should return ``404`` if
        ``MANIFEST_DISABLE_PROFILE_LIST`` setting is ``True``.
        """
        with self.defaults(MANIFEST_DISABLE_PROFILE_LIST=True):
            response = self.client.get(reverse("user_list"))
            self.assertEqual(response.status_code, 404)


class UserDetailViewTests(ManifestTestCase):
    """Tests for :class:`UserDetailView <manifest.views.UserDetailView>`.
    """

    def test_user_detail_view(self):
        """A ``GET`` to the view should render the correct template.
        """
        with self.defaults(MANIFEST_DISABLE_PROFILE_LIST=False):
            response = self.client.get(
                reverse("user_detail", kwargs={"username": "john"})
            )
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, "manifest/user_detail.html")

    def test_user_detail_disabled(self):
        """A ``GET`` to the view should return ``404`` if
        ``MANIFEST_DISABLE_PROFILE_LIST`` setting is ``True``.
        """
        with self.defaults(MANIFEST_DISABLE_PROFILE_LIST=True):
            response = self.client.get(
                reverse("user_detail", kwargs={"username": "john"})
            )
            self.assertEqual(response.status_code, 404)
