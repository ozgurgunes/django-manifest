# -*- coding: utf-8 -*-
""" Manifest Forms
"""

from datetime import datetime

from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q
from django.forms.widgets import ClearableFileInput
from django.utils.translation import ugettext_lazy as _

from manifest import defaults
from manifest.messages import EMAIL_IN_USE_MESSAGE
from manifest.utils import validate_picture

ATTRS_DICT = {"class": "required"}


class LoginForm(forms.Form):
    """
    A custom form where the identification can be a email address or username.

    """

    identification = forms.CharField(
        label=_("Username or Email"),
        widget=forms.TextInput(attrs=ATTRS_DICT),
        max_length=75,
        error_messages={
            "required": _("Please enter your username or email address.")
        },
    )

    password = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(attrs=ATTRS_DICT, render_value=False),
    )

    def __init__(self, *args, **kwargs):
        """
        Custom init to set ``request`` to ``None``.

        """
        self.user_cache = None
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

    def clean(self):
        """
        Checks for the identification and password.

        If the combination can't be found will raise an invalid sign in error.

        """
        identification = self.cleaned_data.get("identification")
        password = self.cleaned_data.get("password")

        if identification and password:
            self.user_cache = authenticate(
                identification=identification, password=password
            )
            if self.user_cache is None:
                raise forms.ValidationError(
                    _("Please check your identification and password.")
                )
        return self.cleaned_data

    def get_user(self):
        """
        Returns user object.
        """
        return self.user_cache


class RegisterForm(UserCreationForm):
    """
    Form for creating a new user account.

    Validates that the requested username and email is not already in use.
    Also requires the password to be entered twice.

    """

    username = forms.RegexField(
        label=_("Username"),
        regex=r"^\w+$",
        max_length=30,
        widget=forms.TextInput(
            attrs=dict(ATTRS_DICT, placeholder=_("Pick a username"))
        ),
        error_messages={
            "invalid": _(
                "Username must contain only letters, numbers and underscores."
            )
        },
    )

    email = forms.EmailField(
        label=_("Email address"),
        widget=forms.TextInput(
            attrs=dict(
                ATTRS_DICT,
                maxlength=75,
                placeholder=_("Enter your email address"),
            )
        ),
    )

    password1 = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(
            attrs=dict(ATTRS_DICT, placeholder=_("Enter a password"))
        ),
    )

    password2 = forms.CharField(
        label=_("Comfirm pasword"),
        widget=forms.PasswordInput(
            attrs=dict(ATTRS_DICT, placeholder=_("Enter password again"))
        ),
    )

    class Meta:
        model = get_user_model()
        fields = ["username", "email", "password1", "password2"]

    def clean_username(self):
        """
        Validate that the username is unique and not listed
        in ``defaults.MANIFEST_FORBIDDEN_USERNAMES`` list.

        """
        try:
            get_user_model().objects.get(
                username=self.cleaned_data["username"]
            )
        except get_user_model().DoesNotExist:
            pass
        else:
            raise forms.ValidationError(
                _("A user with that username already exists.")
            )
        # pylint: disable=bad-continuation
        if (
            self.cleaned_data["username"].lower()
            in defaults.MANIFEST_FORBIDDEN_USERNAMES
        ):
            raise forms.ValidationError(_("This username is not allowed."))
        return self.cleaned_data["username"]

    def clean_email(self):
        """
        Validate that the email address is unique.

        """
        # pylint: disable=bad-continuation
        if get_user_model().objects.filter(
            Q(email__iexact=self.cleaned_data["email"])
            | Q(email_unconfirmed__iexact=self.cleaned_data["email"])
        ):
            raise forms.ValidationError(EMAIL_IN_USE_MESSAGE)
        return self.cleaned_data["email"]

    def save(self, commit=True):
        """
        Creates a new user and account. Returns the newly created user.

        """

        user = get_user_model().objects.create_user(
            self.cleaned_data["username"],
            self.cleaned_data["email"],
            self.cleaned_data["password1"],
            not defaults.MANIFEST_ACTIVATION_REQUIRED,
        )
        return user


class RegisterFormToS(RegisterForm):
    """
    Add a Terms of Service button to the ``RegisterForm``.

    """

    tos = forms.BooleanField(
        widget=forms.CheckboxInput(attrs=ATTRS_DICT),
        label=_("I have read and agree to the Terms of Service."),
        error_messages={
            "required": _("You must agree to the terms to register.")
        },
    )


class EmailChangeForm(forms.Form):
    """
    Form for changing user email address.

    """

    email = forms.EmailField(
        label=_("New email"),
        required=True,
        widget=forms.TextInput(attrs=dict(ATTRS_DICT, maxlength=75)),
    )

    def __init__(self, *args, user=None, **kwargs):
        """
        The current ``user`` is needed for initialisation of this form so
        that we can check if the email address is still free and not always
        returning ``True`` for this query because it's the users own email
        address.

        """
        super().__init__(*args, **kwargs)
        if not isinstance(user, get_user_model()):
            raise TypeError(_("User must be an instance of User"))
        self.user = user

    def clean_email(self):
        """
        Validate that the email is not already registered with another user.

        """
        if self.cleaned_data["email"].lower() == self.user.email:
            raise forms.ValidationError(
                _("You're already known under this email address.")
            )
        # pylint: disable=bad-continuation
        if (
            get_user_model()
            .objects.filter(email__iexact=self.cleaned_data["email"])
            .exclude(email__iexact=self.user.email)
        ):
            raise forms.ValidationError(EMAIL_IN_USE_MESSAGE)
        return self.cleaned_data["email"]

    def save(self):
        """
        Save method calls :func:`user.change_email()` method which sends out
        an email with a verification key to verify and with it enable this
        new email address.

        """
        return self.user.change_email(self.cleaned_data["email"])


class ProfileUpdateForm(forms.ModelForm):
    """ Base form used for fields that are always required """

    GENDER_CHOICES = (("F", _("Female")), ("M", _("Male")))

    first_name = forms.CharField(
        label=_("First name"), max_length=30, required=True
    )
    last_name = forms.CharField(
        label=_("Last name"), max_length=30, required=True
    )

    gender = forms.ChoiceField(
        required=True, choices=GENDER_CHOICES, widget=forms.RadioSelect()
    )
    birth_date = forms.DateField(
        required=True,
        widget=forms.widgets.SelectDateWidget(
            years=range(
                datetime.today().year - 10, datetime.today().year - 99, -1
            )
        ),
    )

    class Meta:
        model = get_user_model()
        fields = ["first_name", "last_name", "gender", "birth_date"]


class RegionUpdateForm(forms.ModelForm):
    """ Base form used for fields that are always required """

    class Meta:
        model = get_user_model()
        fields = ["timezone", "locale"]


class FileInputWidget(ClearableFileInput):
    template_name = "manifest/forms/file_input_widget.html"


class PictureUploadForm(forms.ModelForm):
    """ Base form used for fields that are always required """

    class Meta:
        model = get_user_model()
        fields = [
            # pylint: disable=all # duplicate-code
            "picture"
        ]
        widgets = {"picture": FileInputWidget()}

    def clean_picture(self):
        """
        Validates format and file size of uploaded profile picture.

        """
        return validate_picture(self.cleaned_data.get("picture"), forms)
