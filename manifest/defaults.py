# -*- coding: utf-8 -*-
""" Manifest Defaults
"""

from django.conf import settings
from django.urls import reverse_lazy

MANIFEST_ACTIVATED_LABEL = getattr(
    settings, "MANIFEST_ACTIVATED_LABEL", "ACCOUNT_ACTIVATED"
)

MANIFEST_ACTIVATION_DAYS = getattr(settings, "MANIFEST_ACTIVATION_DAYS", 7)

MANIFEST_ACTIVATION_REQUIRED = getattr(
    settings, "MANIFEST_ACTIVATION_REQUIRED", True
)

MANIFEST_AVATAR_DEFAULT = getattr(
    settings, "MANIFEST_GRAVATAR_DEFAULT", "gravatar"
)

MANIFEST_AVATAR_SIZE = getattr(settings, "MANIFEST_AVATAR_SIZE", 128)


MANIFEST_DISABLE_PROFILE_LIST = getattr(
    settings, "MANIFEST_DISABLE_PROFILE_LIST", False
)

MANIFEST_FORBIDDEN_USERNAMES = getattr(
    settings,
    "MANIFEST_FORBIDDEN_USERNAMES",
    (
        "login",
        "logout",
        "register",
        "activate",
        "signin",
        "signout",
        "signup",
        "me",
        "user",
        "account",
        "email",
        "password",
        "profile",
        "about",
        "contact",
        "test",
    ),
)

MANIFEST_GRAVATAR_DEFAULT = getattr(
    settings, "MANIFEST_GRAVATAR_DEFAULT", "identicon"
)

MANIFEST_LANGUAGE_CODE = getattr(settings, "LANGUAGE_CODE", "en-us")

MANIFEST_LOCALE_FIELD = getattr(settings, "MANIFEST_LOCALE_FIELD", "locale")

MANIFEST_LOGIN_REDIRECT_URL = getattr(
    settings, "MANIFEST_LOGIN_REDIRECT_URL", reverse_lazy("profile_settings")
)

MANIFEST_LOGOUT_ON_GET = getattr(settings, "MANIFEST_LOGOUT_ON_GET", False)

MANIFEST_PICTURE_FORMATS = getattr(
    settings, "MANIFEST_PICTURE_FORMATS", ["jpeg", "gif", "png"]
)

MANIFEST_PICTURE_MAX_FILE = getattr(
    settings, "MANIFEST_PICTURE_MAX_FILE", 1024 * 1024
)

MANIFEST_PICTURE_MAX_SIZE = getattr(
    settings, "MANIFEST_PICTURE_MAX_SIZE", "1024 x 1024"
)

MANIFEST_PICTURE_PATH = getattr(settings, "MANIFEST_PICTURE_PATH", "manifest")


MANIFEST_REDIRECT_ON_LOGOUT = getattr(
    settings, "MANIFEST_REDIRECT_ON_LOGOUT", "/"
)

MANIFEST_REMEMBER_DAYS = getattr(
    settings, "ACCOUNTS_REMEMBER_ME_DAYS", (("a month"), 30)
)

MANIFEST_SESSION_LOGIN = getattr(settings, "MANIFEST_SESSION_LOGIN", True)

MANIFEST_TIME_ZONE = getattr(settings, "TIME_ZONE", "Europe/Istanbul")

MANIFEST_USE_HTTPS = getattr(settings, "MANIFEST_USE_HTTPS", False)

MANIFEST_USE_MESSAGES = getattr(settings, "MANIFEST_USE_MESSAGES", True)
