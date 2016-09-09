from django.conf import settings
from django.test import TestCase
from django.utils.translation import activate, deactivate

class AccountsTestCase(TestCase):
    """ A custom TestCase that loads the accounts application for testing purposes """
    def _pre_setup(self):
        activate(settings.LANGUAGE_CODE)
        super(AccountsTestCase, self)._pre_setup()

    def _post_teardown(self):
        super(AccountsTestCase, self)._post_teardown()
        deactivate()
        