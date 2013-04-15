from django.conf import settings
from django.core.management import call_command
from django.db.models import loading
from django.test import TestCase
from django.utils.translation import activate, deactivate

class ProfileTestCase(TestCase):
    """ A custom TestCase that loads the profile application for testing purposes """
    def _pre_setup(self):
        activate('en-us')
        # Add the models to the db.
        self._original_installed_apps = list(settings.INSTALLED_APPS)
        settings.INSTALLED_APPS += ('manifest.accounts.tests.profiles',)
        loading.cache.loaded = False
        call_command('syncdb', interactive=False, verbosity=0)

        # Call the original method that does the fixtures etc.
        super(ProfileTestCase, self)._pre_setup()

    def _post_teardown(self):
        # Call the original method.
        super(ProfileTestCase, self)._post_teardown()
        # Restore the settings.
        settings.INSTALLED_APPS = self._original_installed_apps
        loading.cache.loaded = False
        deactivate()