# Accounts settings file.
#
# Please consult the docs for more information about each setting.

from django.conf import settings
gettext = lambda s: s


ACCOUNTS_REDIRECT_ON_SIGNOUT = getattr(settings,
                                      'ACCOUNTS_REDIRECT_ON_SIGNOUT',
                                      None)

ACCOUNTS_SIGNIN_REDIRECT_URL = getattr(settings,
                                      'ACCOUNTS_SIGNIN_REDIRECT_URL',
                                      '/accounts/%(username)s/')

ACCOUNTS_ACTIVATION_REQUIRED = getattr(settings,
                                      'ACCOUNTS_ACTIVATION_REQUIRED',
                                      True)

ACCOUNTS_ACTIVATION_DAYS = getattr(settings,
                                  'ACCOUNTS_ACTIVATION_DAYS',
                                  7)

ACCOUNTS_ACTIVATION_NOTIFY = getattr(settings,
                                    'ACCOUNTS_ACTIVATION_NOTIFY',
                                    True)

ACCOUNTS_ACTIVATION_NOTIFY_DAYS = getattr(settings,
                                         'ACCOUNTS_ACTIVATION_NOTIFY_DAYS',
                                         3)

ACCOUNTS_ACTIVATED = getattr(settings,
                            'ACCOUNTS_ACTIVATED',
                            'ALREADY_ACTIVATED')

ACCOUNTS_REMEMBER_ME_DAYS = getattr(settings,
                                   'ACCOUNTS_REMEMBER_ME_DAYS',
                                   (gettext('a month'), 30))

ACCOUNTS_FORBIDDEN_USERNAMES = getattr(settings,
                                      'ACCOUNTS_FORBIDDEN_USERNAMES',
                                      ('register', 'logout', 'login',
                                       'activate', 'me', 'password', 'user'))

ACCOUNTS_USE_HTTPS = getattr(settings,
                            'ACCOUNTS_USE_HTTPS',
                            False)

ACCOUNTS_MUGSHOT_GRAVATAR = getattr(settings,
                                   'ACCOUNTS_MUGSHOT_GRAVATAR',
                                   True)

ACCOUNTS_MUGSHOT_GRAVATAR_SECURE = getattr(settings,
                                          'ACCOUNTS_MUGSHOT_GRAVATAR_SECURE',
                                          ACCOUNTS_USE_HTTPS)

ACCOUNTS_MUGSHOT_DEFAULT = getattr(settings,
                                  'ACCOUNTS_MUGSHOT_DEFAULT',
                                  'identicon')

ACCOUNTS_MUGSHOT_SIZE = getattr(settings,
                               'ACCOUNTS_MUGSHOT_SIZE',
                               128)

ACCOUNTS_MUGSHOT_CROP_TYPE = getattr(settings,
                                    'ACCOUNTS_MUGSHOT_CROP_TYPE',
                                    'smart')

ACCOUNTS_MUGSHOT_PATH = getattr(settings,
                               'ACCOUNTS_MUGSHOT_PATH',
                               'mugshots/')

ACCOUNTS_DEFAULT_PRIVACY = getattr(settings,
                                  'ACCOUNTS_DEFAULT_PRIVACY',
                                  'registered')

ACCOUNTS_DISABLE_PROFILE_LIST = getattr(settings,
                                       'ACCOUNTS_DISABLE_PROFILE_LIST',
                                       False)

ACCOUNTS_USE_MESSAGES = getattr(settings,
                               'ACCOUNTS_USE_MESSAGES',
                               False)

ACCOUNTS_LANGUAGE_FIELD = getattr(settings,
                                 'ACCOUNTS_LANGUAGE_FIELD',
                                 'language')

ACCOUNTS_WITHOUT_USERNAMES = getattr(settings,
                                    'ACCOUNTS_WITHOUT_USERNAMES',
                                    False)

ACCOUNTS_PROFILE_DETAIL_TEMPLATE = getattr(
    settings, 'ACCOUNTS_PROFILE_DETAIL_TEMPLATE', 'accounts/profile_detail.html')

ACCOUNTS_HIDE_EMAIL = getattr(settings, 'ACCOUNTS_HIDE_EMAIL', True)
