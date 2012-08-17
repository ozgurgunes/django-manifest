from django.test import TestCase
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from manifest.accounts.backends import AuthenticationBackend

class AuthenticationBackendTests(TestCase):
    """
    Test the ``AuthenticationBackend`` which should return a ``User``
    when supplied with a username/email and a correct password.

    """
    fixtures = ['test']
    backend = AuthenticationBackend()

    def test_with_username(self):
        """ Test the backend when usernames are supplied. """
        # Invalid usernames or passwords
        invalid_data_dicts = [
            # Invalid password
            {'identification': 'john',
             'password': 'invalid'},
            # Invalid username
            {'identification': 'foo',
             'password': 'pass'},
        ]
        for invalid_dict in invalid_data_dicts:
            result = self.backend.authenticate(
                            identification=invalid_dict['identification'],
                            password=invalid_dict['password'])
            self.failIf(isinstance(result, User))

        # Valid username and password
        result = self.backend.authenticate(identification='john',
                                           password='pass')
        self.failUnless(isinstance(result, User))

    def test_with_email(self):
        """ Test the backend when email address is supplied """
        # Invalid e-mail adressses or passwords
        invalid_data_dicts = [
            # Invalid password
            {'identification': 'john@example.com',
             'password': 'invalid'},
            # Invalid e-mail address
            {'identification': 'foo@example.com',
             'password': 'pass'},
        ]
        for invalid_dict in invalid_data_dicts:
            result = self.backend.authenticate(
                                identification=invalid_dict['identification'],
                                password=invalid_dict['password'])
            self.failIf(isinstance(result, User))

        # Valid e-email address and password
        result = self.backend.authenticate(identification='john@example.com',
                                           password='pass')
        self.failUnless(isinstance(result, User))

    def test_get_user(self):
        """ Test that the user is returned """
        user = self.backend.get_user(1)
        self.failUnlessEqual(user.username, 'john')

        # None should be returned when false id.
        user = self.backend.get_user(99)
        self.failIf(user)