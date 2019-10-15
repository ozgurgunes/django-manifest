# -*- coding: utf-8 -*-
""" Manifest Utilities
"""

import datetime
import hashlib
import random
import urllib

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from manifest import defaults


def jwt_encode(user):
    from rest_framework_jwt.settings import api_settings

    jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
    jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

    payload = jwt_payload_handler(user)
    return jwt_encode_handler(payload)


def get_image_path(instance, filename):
    """
    Uploads a picture for a user to the ``MANIFEST_PICTURE_PATH`` and
    saving it under unique hash for the image. This is for privacy
    reasons so others can't just browse through the picture directory.

    """
    extension = filename.split(".")[-1].lower()
    key = generate_sha1(
        "_".join([str(datetime.datetime.now()), str(instance.id)])
    )
    return "%(path)s/%(key)s.%(extension)s" % {
        "path": getattr(
            defaults,
            "MANIFEST_PICTURE_PATH",
            "%s/%s"
            % (str(instance._meta.app_label), str(instance._meta.model_name)),
        ),
        "key": key[1],
        "extension": extension,
    }


def validate_picture(file, handler):
    if file:
        content_type = getattr(file, "content_type", None)
        if content_type:
            main, sub = content_type.split("/")
            # pylint: disable=bad-continuation
            if not (
                main == "image" and sub in defaults.MANIFEST_PICTURE_FORMATS
            ):
                raise handler.ValidationError(
                    _("%s only." % defaults.MANIFEST_PICTURE_FORMATS)
                )
        if file.size > int(defaults.MANIFEST_PICTURE_MAX_FILE):
            raise handler.ValidationError(_("Image size is too big."))
        return file
    if file is None:
        # User has no existing profile picture and submitting empty form.
        raise handler.ValidationError(_("This field is required."))
    return file


def get_gravatar(email):
    """ Get's the Gravatar for a email address.

    :param email:
        The email that will be hashed to get the Gravatar.

    :return: The URI pointing to the Gravatar.

    """
    url = "http"
    if defaults.MANIFEST_USE_HTTPS:
        url += "s"
    url += "://www.gravatar.com/avatar/"

    gravatar = "%(url)s%(id)s?" % {
        "url": url,
        "id": hashlib.md5(email.lower().encode("utf-8")).hexdigest(),
    }

    gravatar += urllib.parse.urlencode(
        {
            "s": str(defaults.MANIFEST_AVATAR_SIZE),
            "d": defaults.MANIFEST_GRAVATAR_DEFAULT,
        }
    )
    return gravatar


def get_login_redirect(redirect=None):
    """
    Redirect user after successful login.

    Returns ``redirect`` parameter if it exists and resolved, else
    ``MANIFEST_LOGIN_REDIRECT_URL`` setting.

    :param redirect:
        A URL usually supplied by ``next`` form field.

    :return: String containing the URL for redirect to.

    """
    return redirect if redirect else defaults.MANIFEST_LOGIN_REDIRECT_URL


def generate_sha1(string, salt=None):
    """
    Generates a sha1 hash for supplied string. Doesn't need to be very secure
    because it's not used for password checking. We got Django for that.

    :param string:
        The string that needs to be encrypted.

    :param salt:
        Optionally define your own salt. If none is supplied, will use a
        random string of 5 characters.

    :return: Tuple containing the salt and hash.

    """
    if not salt:
        salt = hashlib.sha1(  # noqa
            str(random.random()).encode("utf-8")  # noqa
        ).hexdigest()[:5]
    key = hashlib.sha1(
        (salt + str(string)).encode("utf-8")
    ).hexdigest()  # noqa

    return (salt, key)


def get_protocol():
    """
    Returns a string with the current protocol.

    This can be either 'http' or 'https' depending on ``MANIFEST_USE_HTTPS``
    setting.

    """
    protocol = "http"
    if getattr(settings, "MANIFEST_USE_HTTPS", defaults.MANIFEST_USE_HTTPS):
        protocol = "https"
    return protocol
