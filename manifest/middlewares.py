# -*- coding: utf-8 -*-
""" Manifest Middlewares
"""

from django.conf import settings
from django.middleware.locale import LocaleMiddleware as DjangoLocaleMiddleware
from django.utils import translation

from manifest import defaults


class LocaleMiddleware(DjangoLocaleMiddleware):
    """
    Set the language by looking at the language setting in the profile.

    It doesn't override the cookie that is set by Django so a user can still
    switch languages depending if the cookie is set.

    """

    def process_request(self, request):
        lang_cookie = request.session.get(settings.LANGUAGE_COOKIE_NAME)
        if not lang_cookie:
            if request.user.is_authenticated:
                try:
                    lang = getattr(request.user, defaults.MANIFEST_LOCALE_FIELD)
                    translation.activate(lang)
                    request.LANGUAGE_CODE = translation.get_language()
                except AttributeError:
                    pass
