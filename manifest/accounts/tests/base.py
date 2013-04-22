from django.conf import settings
from django.core.management import call_command
from django.db.models import loading
from django.test import TestCase
from django.utils.translation import activate, deactivate

from sorl.thumbnail.conf import settings as sorl

class AccountsTestCase(TestCase):
    """ A custom TestCase that loads the accounts application for testing purposes """
    def _pre_setup(self):
        activate('tr-tr')
        self._sorl = sorl.THUMBNAIL_DEBUG
        sorl.THUMBNAIL_DEBUG = False
        super(AccountsTestCase, self)._pre_setup()

    def _post_teardown(self):
        super(AccountsTestCase, self)._post_teardown()
        sorl.THUMBNAIL_DEBUG = self._sorl
        deactivate()
        