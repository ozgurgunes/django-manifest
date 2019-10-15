# -*- coding: utf-8 -*-
""" Manifest Form Tests
"""


from django.contrib.auth import get_user_model
from django.forms import Form, ModelForm

from manifest import forms
from tests import data_dicts
from tests.base import ManifestTestCase, ManifestUploadTestCase


class ManifestFormTestCase(ManifestTestCase):
    """Test case for forms.
    """

    user = None
    form_class = Form
    data_dicts = {"invalid": [], "valid": []}

    def invalid_test(self):
        """An invalid form should raise ``ValidationError``.
        """
        for invalid_dict in self.data_dicts["invalid"]:
            if self.user:
                if issubclass(self.form_class, ModelForm):
                    form = self.form_class(self.user, invalid_dict["data"])
                else:
                    form = self.form_class(
                        user=self.user, data=invalid_dict["data"]
                    )
            else:
                form = self.form_class(data=invalid_dict["data"])
            self.assertFalse(form.is_valid())
            self.assertEqual(
                form.errors[invalid_dict["error"][0]], invalid_dict["error"][1]
            )

    def valid_test(self):
        """An valid form should return ``True``.
        """
        for valid_dict in self.data_dicts["valid"]:
            if self.user:
                if issubclass(self.form_class, ModelForm):
                    form = self.form_class(self.user, valid_dict)
                else:
                    form = self.form_class(user=self.user, data=valid_dict)
            else:
                form = self.form_class(data=valid_dict)

            self.assertTrue(form.is_valid())


class LoginFormTests(ManifestFormTestCase):
    """Tests for :class:`LoginForm <manifest.forms.LoginForm>`.
    """

    form_class = forms.LoginForm
    data_dicts = data_dicts.LOGIN_FORM

    def test_invalid_form(self):
        self.invalid_test()

    def test_valid_form(self):
        self.valid_test()


class RegisterFormTests(ManifestFormTestCase):
    """Tests for :class:`RegisterForm <manifest.forms.RegisterForm>`.
    """

    form_class = forms.RegisterForm
    data_dicts = data_dicts.REGISTER_FORM

    def test_invalid_form(self):
        self.invalid_test()

    def test_valid_form(self):
        self.valid_test()


class EmailChangeFormTests(ManifestFormTestCase):
    """Tests for :class:`EmailChangeForm <manifest.forms.EmailChangeForm>`.
    """

    form_class = forms.EmailChangeForm
    data_dicts = data_dicts.EMAIL_CHANGE_FORM

    def setUp(self):
        self.user = get_user_model().objects.get(pk=1)
        super(EmailChangeFormTests, self).setUp()

    def test_form_init(self):
        """ The form must be initialized with a ``User`` instance. """
        self.assertRaises(TypeError, forms.EmailChangeForm, None)

    def test_invalid_form(self):
        self.invalid_test()

    def test_valid_form(self):
        self.valid_test()


class ProfileUpdateFormTests(ManifestFormTestCase):
    """Tests for :class:`ProfileUpdateForm <manifest.forms.ProfileUpdateForm>`.
    """

    form_class = forms.ProfileUpdateForm
    data_dicts = data_dicts.PROFILE_UPDATE_FORM

    def test_invalid_form(self):
        self.invalid_test()

    def test_valid_form(self):
        self.valid_test()


# pylint: disable=too-many-ancestors
class PictureUploadFormTests(ManifestFormTestCase, ManifestUploadTestCase):
    """Tests for :class:`ProfileUpdateForm <manifest.forms.ProfileUpdateForm>`.
    """

    form_class = forms.PictureUploadForm
    data_dicts = None

    def setUp(self):
        self.user = [get_user_model().objects.get(pk=1)]
        super().setUp()
        self.data_dicts = data_dicts.picture_upload_form(self)

    def test_invalid_form(self):
        self.invalid_test()

    def test_valid_form(self):
        self.valid_test()

    def test_file_size(self):
        with self.upload_limit():
            form = self.form_class(
                self.user, self.data_dicts["invalid_file_size"]["data"]
            )
            form.is_valid()
            self.assertEqual(
                form.errors[self.data_dicts["invalid_file_size"]["error"][0]],
                self.data_dicts["invalid_file_size"]["error"][1],
            )

    def test_file_type(self):
        form = self.form_class(
            self.user, self.data_dicts["invalid_file_type"]["data"]
        )
        form.is_valid()
        self.assertEqual(
            form.errors[self.data_dicts["invalid_file_type"]["error"][0]],
            self.data_dicts["invalid_file_type"]["error"][1],
        )

    def test_file_extension(self):
        form = self.form_class(
            self.user, self.data_dicts["invalid_file_extension"]["data"]
        )
        form.is_valid()
        self.assertTrue(
            "File extension “svg” is not allowed."
            in form.errors[
                self.data_dicts["invalid_file_extension"]["error"][0]
            ][0]
        )


class RegionUpdateFormTests(ManifestFormTestCase):
    """Tests for :class:`ProfileUpdateForm <manifest.forms.ProfileUpdateForm>`.
    """

    form_class = forms.RegionUpdateForm
    data_dicts = data_dicts.REGION_UPDATE_FORM

    def test_invalid_form(self):
        self.invalid_test()

    def test_valid_form(self):
        self.valid_test()
