# -*- coding: utf-8 -*-
""" Manifest Messages
"""

from django.utils.translation import ugettext as _

AUTH_LOGIN_SUCCESS = _("User logged in.")
AUTH_LOGOUT_SUCCESS = _("User logged out.")
AUTH_REGISTER_SUCCESS = _("User registered.")
AUTH_REGISTER_ERROR = _("Registration failed.")
AUTH_REGISTER_FORBIDDEN = _("Registration forbidden.")
AUTH_ACTIVATE_SUCCESS = _("Account activated.")
AUTH_ACTIVATE_ERROR = _("Activation failed!")
PASSWORD_RESET_SUCCESS = _("Password reset sent.")
PASSWORD_RESET_VERIFY_SUCCESS = _("Token verified.")
PASSWORD_RESET_VERIFY_ERROR = _("Verification failed.")
PASSWORD_RESET_CONFIRM_SUCCESS = _("New password saved.")
PASSWORD_RESET_CONFIRM_ERROR = _("Password reset failed.")
PASSWORD_CHANGE_SUCCESS = _("Password changed.")
EMAIL_CHANGE_SUCCESS = _("Email changed.")
EMAIL_CHANGE_CONFIRM_SUCCESS = _("Email confirmed.")
EMAIL_CHANGE_CONFIRM_ERROR = _("Confirmation failed.")
PROFILE_UPDATE_SUCCESS = _("Profile updated.")
REGION_UPDATE_SUCCESS = _("Regional settings updated.")
PICTURE_UPLOAD_SUCCESS = _("Picture uploaded.")

EMAIL_IN_USE_MESSAGE = _(
    "This email address is already in use. Please supply a different email."
)
