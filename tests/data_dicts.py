# -*- coding: utf-8 -*-
""" Manifest Data Dicts for Tests
"""

from django.utils.translation import ugettext_lazy as _

from manifest import defaults

LOGIN_FORM = {
    "invalid": [
        # No identification.
        {
            "data": {"identification": "", "password": "inhalefish"},
            "error": (
                "identification",
                [_("Please enter your username or email address.")],
            ),
        },
        # No password.
        {
            "data": {"identification": "john", "password": ""},
            "error": ("password", [_("This field is required.")]),
        },
        # Wrong user.
        {
            "data": {"identification": "johnn", "password": "pass"},
            "error": (
                "__all__",
                [_("Please check your identification and password.")],
            ),
        },
        # Wrong password.
        {
            "data": {"identification": "john", "password": "passs"},
            "error": (
                "__all__",
                [_("Please check your identification and password.")],
            ),
        },
    ],
    "valid": [
        {"identification": "john", "password": "pass"},
        {"identification": "john@example.com", "password": "pass"},
    ],
}

LOGIN_SERIALIZER = {
    "invalid": [
        # No identification.
        {
            "data": {"identification": "", "password": "inhalefish"},
            "error": ("identification", [_("This field may not be blank.")]),
        },
        # No password.
        {
            "data": {"identification": "john", "password": ""},
            "error": ("password", [_("This field may not be blank.")]),
        },
        # Wrong user.
        {
            "data": {"identification": "johnn", "password": "pass"},
            "error": (
                "non_field_errors",
                [_("Please check your identification and password.")],
            ),
        },
        # Wrong password.
        {
            "data": {"identification": "john", "password": "passs"},
            "error": (
                "non_field_errors",
                [_("Please check your identification and password.")],
            ),
        },
    ],
    "valid": [
        {"identification": "john", "password": "pass"},
        {"identification": "john@example.com", "password": "pass"},
    ],
}

REGISTER_FORM = {
    "invalid": [
        # Non-alphanumeric username.
        {
            "data": {
                "username": "foo@bar",
                "email": "foo@example.com",
                "password": "foo",
                "password2": "foo",
                "tos": "on",
            },
            "error": (
                "username",
                [
                    _(
                        "Username must contain only letters, "
                        "numbers and underscores."
                    )
                ],
            ),
        },
        # Passwords are not same.
        {
            "data": {
                "username": "foo2bar",
                "email": "bar@example.com",
                "password1": "foo",
                "password2": "foo2",
                "tos": "on",
            },
            "error": (
                "password2",
                [_("The two password fields didn’t match.")],
            ),
        },
        # Already taken username.
        {
            "data": {
                "username": "john",
                "email": "johndoe@example.com",
                "password1": "foo",
                "password2": "foo",
                "tos": "on",
            },
            "error": (
                "username",
                [_("A user with that username already exists.")],
            ),
        },
        # Already taken email.
        {
            "data": {
                "username": "johndoe",
                "email": "john@example.com",
                "password": "foo",
                "password2": "foo",
                "tos": "on",
            },
            "error": (
                "email",
                [
                    _(
                        "This email address is already in use. "
                        "Please supply a different email."
                    )
                ],
            ),
        },
        # Forbidden username.
        {
            "data": {
                "username": "test",
                "email": "test@example.com",
                "password": "foo",
                "password2": "foo2",
                "tos": "on",
            },
            "error": ("username", [_("This username is not allowed.")]),
        },
    ],
    "valid": [
        {
            "username": "alice",
            "email": "alice@example.com",
            "password1": "wonderland",
            "password2": "wonderland",
            "tos": "on",
        }
    ],
}

REGISTER_SERIALIZER = {
    "invalid": [
        # Non-alphanumeric username.
        {
            "data": {
                "username": "foo@bar",
                "email": "foo@example.com",
                "password": "foo",
                "password2": "foo",
                "tos": "on",
            },
            "error": (
                "username",
                [
                    _(
                        "Username must contain only letters, "
                        "numbers and underscores."
                    )
                ],
            ),
        },
        # Passwords are not same.
        {
            "data": {
                "username": "foo2bar",
                "email": "bar@example.com",
                "password1": "foo",
                "password2": "foo2",
                "tos": "on",
            },
            "error": (
                "password1",
                [_("The two password fields didn’t match.")],
            ),
        },
        # Already taken username.
        {
            "data": {
                "username": "john",
                "email": "johndoe@example.com",
                "password1": "foo",
                "password2": "foo",
                "tos": "on",
            },
            "error": (
                "username",
                [_("A user with that username already exists.")],
            ),
        },
        # Already taken email.
        {
            "data": {
                "username": "johndoe",
                "email": "john@example.com",
                "password": "foo",
                "password2": "foo",
                "tos": "on",
            },
            "error": (
                "email",
                [
                    _(
                        "This email address is already in use. "
                        "Please supply a different email."
                    )
                ],
            ),
        },
        # Forbidden username.
        {
            "data": {
                "username": "test",
                "email": "test@example.com",
                "password": "foo",
                "password2": "foo2",
                "tos": "on",
            },
            "error": ("username", [_("This username is not allowed.")]),
        },
    ],
    "valid": [
        {
            "username": "foobar",
            "email": "foobar@example.com",
            "password1": "foo",
            "password2": "foo",
            "tos": "on",
        }
    ],
}

PROFILE_UPDATE_FORM = {
    "invalid": [
        # Invalid name.
        {
            "data": {
                "first_name": "",
                "last_name": "",
                "gender": "M",
                "birth_date": "1970-01-01",
            },
            "error": ("first_name", [_("This field is required.")]),
        },
        # Invalid gender.
        {
            "data": {
                "first_name": "John",
                "last_name": "Smith",
                "gender": "",
                "birth_date": "1970-01-01",
            },
            "error": ("gender", [_("This field is required.")]),
        },
        # Invalid birth date.
        {
            "data": {
                "first_name": "John",
                "last_name": "Smith",
                "gender": "M",
                "birth_date": "",
            },
            "error": ("birth_date", [_("This field is required.")]),
        },
    ],
    "valid": [
        {
            "first_name": "John",
            "last_name": "Smith",
            "gender": "M",
            "birth_date": "1970-01-01",
        },
        {
            "first_name": "Jane",
            "last_name": "Smith",
            "gender": "F",
            "birth_date": "1970-01-01",
        },
    ],
}


PROFILE_UPDATE_SERIALIZER = {
    "invalid": [
        # Invalid name.
        {
            "data": {
                "first_name": "",
                "last_name": "",
                "gender": "M",
                "birth_date": "01/01/1970",
            },
            "error": ("first_name", [_("This field may not be blank.")]),
        },
        # Invalid gender.
        {
            "data": {
                "first_name": "John",
                "last_name": "Smith",
                "gender": "",
                "birth_date": "01/01/1970",
            },
            "error": ("gender", [_('"" is not a valid choice.')]),
        },
    ],
    "valid": [
        {
            "first_name": "John",
            "last_name": "Smith",
            "gender": "M",
            "birth_date": "01/01/1970",
        },
        {
            "first_name": "Jane",
            "last_name": "Smith",
            "gender": "F",
            "birth_date": "01/01/1970",
        },
    ],
}


EMAIL_CHANGE_FORM = {
    "invalid": [
        # No change in e-mail address.
        {
            "data": {"email": "john@example.com"},
            "error": (
                "email",
                [_("You're already known under this email address.")],
            ),
        },
        # An e-mail address used by another user.
        {
            "data": {"email": "jane@example.com"},
            "error": (
                "email",
                [
                    _(
                        "This email address is already in use. "
                        "Please supply a different email."
                    )
                ],
            ),
        },
    ],
    "valid": [{"email": "john.smith@example.com"}],
}


EMAIL_CHANGE_SERIALIZER = {
    "invalid": [
        # No change in e-mail address.
        {
            "data": {"email": "john@example.com"},
            "error": (
                "email",
                [_("You're already known under this email address.")],
            ),
        },
        # An e-mail address used by another.
        {
            "data": {"email": "jane@example.com"},
            "error": (
                "email",
                [
                    _(
                        "This email address is already in use. "
                        "Please supply a different email."
                    )
                ],
            ),
        },
    ],
    "valid": [{"email": "john.smith@example.com"}],
}


REGION_UPDATE_FORM = {
    "invalid": [
        # Invalid timezone.
        {
            "data": {"timezone": "test1", "locale": "tr"},
            "error": (
                "timezone",
                [
                    _(
                        "Select a valid choice. "
                        "test1 is not one of the available choices."
                    )
                ],
            ),
        },
        # Invalid locale.
        {
            "data": {"timezone": "Europe/Istanbul", "locale": "test2"},
            "error": (
                "locale",
                [
                    _(
                        "Select a valid choice. "
                        "test2 is not one of the available choices."
                    )
                ],
            ),
        },
    ],
    "valid": [
        {"timezone": "Europe/Istanbul", "locale": "tr"},
        {"timezone": "UTC", "locale": "en"},
    ],
}

REGION_UPDATE_SERIALIZER = {
    "invalid": [
        # Invalid timezone.
        {
            "data": {"timezone": "test1", "locale": "tr"},
            "error": ("timezone", [_('"test1" is not a valid choice.')]),
        },
        # Invalid locale.
        {
            "data": {"timezone": "Europe/Istanbul", "locale": "test2"},
            "error": ("locale", [_('"test2" is not a valid choice.')]),
        },
    ],
    "valid": [
        {"timezone": "Europe/Istanbul", "locale": "tr"},
        {"timezone": "UTC", "locale": "en"},
    ],
}

PASSWORD_RESET_SERIALIZER = {
    "invalid": [
        # No email.
        {
            "data": {"email": ""},
            "error": ("email", [_("This field may not be blank.")]),
        },
        # Invalid email.
        {
            "data": {"email": "test.com"},
            "error": ("email", [_("Enter a valid email address.")]),
        },
    ],
    "valid": [{"email": "john@exmple.com"}],
}

PASSWORD_CHANGE_FORM = {
    "invalid": [
        # Wrong old password.
        {
            "data": {
                "old_password": "pass1",
                "new_password1": "newpass",
                "new_password2": "newpass",
            },
            "error": (
                "old_password",
                [
                    _(
                        "Your old password was entered incorrectly. "
                        "Please enter it again."
                    )
                ],
            ),
        },
        # Invalid email.
        {
            "data": {
                "old_password": "pass",
                "new_password1": "newpass1",
                "new_password2": "newpass2",
            },
            "error": (
                "new_password2",
                [_("The two password fields didn’t match.")],
            ),
        },
    ],
    "valid": [
        {
            "old_password": "pass",
            "new_password1": "newpass",
            "new_password2": "newpass",
        }
    ],
}


PASSWORD_CHANGE_SERIALIZER = {
    "invalid": [
        # Wrong old password.
        {
            "data": {
                "old_password": "pass1",
                "new_password1": "newpass",
                "new_password2": "newpass",
            },
            "error": (
                "old_password",
                [
                    _(
                        "Your old password was entered incorrectly. "
                        "Please enter it again."
                    )
                ],
            ),
        },
        # Invalid email.
        {
            "data": {
                "old_password": "pass",
                "new_password1": "newpass1",
                "new_password2": "newpass2",
            },
            "error": (
                "new_password2",
                [_("The two password fields didn’t match.")],
            ),
        },
    ],
    "valid": [
        {
            "old_password": "pass",
            "new_password1": "newpass",
            "new_password2": "newpass",
        }
    ],
}


def picture_upload_form(self):
    return {
        "invalid": [
            {
                "data": {"picture": None},
                "error": ("picture", [_("This field is required.")]),
            },
            {
                "data": {"picture": object},
                "error": (
                    "picture",
                    [
                        _(
                            "No file was submitted. "
                            "Check the encoding type on the form."
                        )
                    ],
                ),
            },
        ],
        "invalid_file_size": {
            "data": {"picture": self.raw_image_file},
            "error": ("picture", [_("Image size is too big.")]),
        },
        "invalid_file_type": {
            "data": {
                "picture": self.get_raw_file(
                    self.create_image(".tiff", "TIFF")
                )
            },
            "error": (
                "picture",
                [_("%s only." % defaults.MANIFEST_PICTURE_FORMATS)],
            ),
        },
        "invalid_file_extension": {
            "data": {
                "picture": self.get_raw_file(self.create_image(".svg", "TIFF"))
            },
            "error": ("picture", [_("File extension “svg” is not allowed.")]),
        },
        "valid": [{"picture": self.raw_image_file}],
    }


def picture_upload_serializer(self):
    return {
        "invalid": [
            {
                "data": {"picture": None},
                "error": ("picture", [_("This field may not be null.")]),
            },
            {
                "data": {"picture": object},
                "error": (
                    "picture",
                    [
                        _(
                            "The submitted data was not a file. "
                            "Check the encoding type on the form."
                        )
                    ],
                ),
            },
        ],
        "invalid_file_size": {
            "data": {"picture": self.image_file},
            "error": (
                "picture",
                [
                    _(
                        "The submitted data was not a file. "
                        "Check the encoding type on the form."
                    )
                ],
            ),
        },
        "invalid_file_type": {
            "data": {
                "picture": self.get_raw_file(
                    self.create_image(".tiff", "TIFF")
                )
            },
            "error": (
                "picture",
                [_("%s only." % defaults.MANIFEST_PICTURE_FORMATS)],
            ),
        },
        "invalid_file_extension": {
            "data": {
                "picture": self.get_raw_file(self.create_image(".svg", "TIFF"))
            },
            "error": ("picture", [_("File extension “svg” is not allowed.")]),
        },
        "valid": [{"picture": self.raw_image_file}],
    }
