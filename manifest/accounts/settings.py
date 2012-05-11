# -*- coding: utf-8 -*-
# Accounts settings file.
#
# Please consult the docs for more information about each setting.

from django.conf import settings
gettext = lambda s: s


ACCOUNTS_REDIRECT_ON_LOGOUT = getattr(settings,
                                      'ACCOUNTS_REDIRECT_ON_LOGOUT',
                                      None)

ACCOUNTS_LOGIN_REDIRECT_URL = getattr(settings,
                                      'ACCOUNTS_LOGIN_REDIRECT_URL',
                                      getattr(settings, 'LOGIN_REDIRECT_URL', '/accounts/%(username)s/'))

ACCOUNTS_ACTIVATION_REQUIRED = getattr(settings,
                                      'ACCOUNTS_ACTIVATION_REQUIRED',
                                      True)

ACCOUNTS_ACTIVATION_DAYS = getattr(settings,
                                  'ACCOUNTS_ACTIVATION_DAYS',
                                  7)

ACCOUNTS_ACTIVATED = getattr(settings,
                            'ACCOUNTS_ACTIVATED',
                            'ALREADY_ACTIVATED')

ACCOUNTS_REMEMBER_ME_DAYS = getattr(settings,
                                   'ACCOUNTS_REMEMBER_ME_DAYS',
                                   (gettext('a month'), 30))

ACCOUNTS_FORBIDDEN_USERNAMES = getattr(settings,
                                      'ACCOUNTS_FORBIDDEN_USERNAMES',
                                      ('register', 'activate', 'logout', 'login', 'me', 
                                       'user', 'password', 'account', 'profile'))

ACCOUNTS_USE_HTTPS = getattr(settings,
                            'ACCOUNTS_USE_HTTPS',
                            False)

ACCOUNTS_PICTURE_MAX_SIZE = getattr(settings,
                                   'ACCOUNTS_PICTURE_MAX_SIZE',
                                   '1024 x 1024')

ACCOUNTS_PICTURE_PATH = getattr(settings,
                               'ACCOUNTS_GRAVATAR_PATH',
                               'accounts')

ACCOUNTS_PICTURE_FORMATS = getattr(settings,
                                   'ACCOUNTS_PICTURE_FORMATS',
                                   ['jpeg', 'gif', 'png'])

ACCOUNTS_PICTURE_MAX_FILE = getattr(settings,
                                   'ACCOUNTS_PICTURE_MAX_FILE',
                                   1024*1024)

ACCOUNTS_GRAVATAR_MAX_FILE = getattr(settings,
                                   'ACCOUNTS_PICTURE_MAX_FILE',
                                   1024*1024)

ACCOUNTS_GRAVATAR_PICTURE = getattr(settings,
                                   'ACCOUNTS_GRAVATAR_PICTURE',
                                   True)

ACCOUNTS_GRAVATAR_SECURE = getattr(settings,
                                          'ACCOUNTS_GRAVATAR_SECURE',
                                          ACCOUNTS_USE_HTTPS)

ACCOUNTS_GRAVATAR_DEFAULT = getattr(settings,
                                  'ACCOUNTS_GRAVATAR_DEFAULT',
                                  'identicon')

ACCOUNTS_GRAVATAR_SIZE = getattr(settings,
                               'ACCOUNTS_GRAVATAR_SIZE',
                               128)

ACCOUNTS_DISABLE_PROFILE_LIST = getattr(settings,
                                       'ACCOUNTS_DISABLE_PROFILE_LIST',
                                       False)

ACCOUNTS_USE_MESSAGES = getattr(settings,
                               'ACCOUNTS_USE_MESSAGES',
                               False)

ACCOUNTS_LOCALE_FIELD = getattr(settings,
                                 'ACCOUNTS_LOCALE_FIELD',
                                 'locale')

ACCOUNTS_WITHOUT_USERNAMES = getattr(settings,
                                    'ACCOUNTS_WITHOUT_USERNAMES',
                                    False)

ACCOUNTS_HIDE_EMAIL = getattr(settings, 'ACCOUNTS_HIDE_EMAIL', True)
