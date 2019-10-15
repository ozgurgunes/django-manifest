# -*- coding: utf-8 -*-
""" Manifest Decorators
"""

from functools import wraps

from django.conf import settings
from django.http import HttpResponsePermanentRedirect

from manifest import defaults


def secure_required(view_func):
    """
    Decorator that redirects to a secure version (https) of the url.

    If ``MANIFEST_USE_HTTPS`` setting is ``True``, any view this decorator
    applied and accessed through an insecure (http) protocol, will return
    a permanent redirect to the secure (https) version of itself.

    """

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not settings.DEBUG and not request.is_secure():
            if defaults.MANIFEST_USE_HTTPS:
                request_url = request.build_absolute_uri(
                    request.get_full_path()
                )
                secure_url = request_url.replace("http://", "https://")
                return HttpResponsePermanentRedirect(secure_url)
        return view_func(request, *args, **kwargs)

    return _wrapped_view
