# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

from manifest.accounts import forms
from manifest.accounts import defaults
from manifest.accounts.tests.base import AccountsTestCase

class RegistrationFormTests(AccountsTestCase):
    """ Test the registration form. """
    fixtures = ['test']

    def test_registration_form(self):
        """
        Test that the ``RegistrationForm`` checks for unique usernames 
        and unique e-mail addresses.

        """
        invalid_data_dicts = [
            # Non-alphanumeric username.
            {'data': {'username': 'foo@bar',
                      'email': 'foo@example.com',
                      'password': 'foo',
                      'password2': 'foo',
                      'tos': 'on'},
             'error': ('username', [_(u'Username must contain only letters, numbers and underscores.')])},
             
            # Password is not the same
            {'data': {'username': 'foo2bar',
                      'email': 'bar@example.com',
                      'password1': 'foo',
                      'password2': 'foo2',
                      'tos': 'on'},
             'error': ('password2', [_("The two password fields didn't match.")])},

            # Already taken username
            {'data': {'username': 'john',
                      'email': 'johndoe@example.com',
                      'password1': 'foo',
                      'password2': 'foo',
                      'tos': 'on'},
             'error': ('username', [_(u'A user with that username already exists.')])},

            # Already taken email
            {'data': {'username': 'johndoe',
                      'email': 'john@example.com',
                      'password': 'foo',
                      'password2': 'foo',
                      'tos': 'on'},
             'error': ('email', [_(u'This email address is already in use. Please supply a different email.')])},

            # Forbidden username
            {'data': {'username': 'register',
                      'email': 'register@example.com',
                      'password': 'foo',
                      'password2': 'foo2',
                      'tos': 'on'},
             'error': ('username', [_(u'This username is not allowed.')])},
        ]

        for invalid_dict in invalid_data_dicts:
            form = forms.RegistrationForm(data=invalid_dict['data'])
            self.failIf(form.is_valid())
            self.assertEqual(form.errors[invalid_dict['error'][0]],
                             invalid_dict['error'][1])


        # And finally, a valid form.
        form = forms.RegistrationForm(data={'username': 'foobar',
                                      'email': 'foobar@example.com',
                                      'password1': 'foo',
                                      'password2': 'foo',
                                      'tos': 'on'})

        self.failUnless(form.is_valid())

class AuthenticationFormTests(AccountsTestCase):
    """ Test the ``AuthenticationForm`` """

    fixtures = ['test']

    def test_authentication_form(self):
        """
        Check that the ``AuthenticationForm`` requires both identification and password

        """
        invalid_data_dicts = [
            {'data': {'identification': '',
                      'password': 'inhalefish'},
             'error': ('identification', [_(u"Either supply us with your email or username.")])},
            {'data': {'identification': 'john',
                      'password': 'inhalefish'},
             'error': ('__all__', [_(u"Please enter a correct username or email address and password. Note that both fields are case-sensitive.")])}
        ]

        for invalid_dict in invalid_data_dicts:
            form = forms.AuthenticationForm(data=invalid_dict['data'])
            self.failIf(form.is_valid())
            self.assertEqual(form.errors[invalid_dict['error'][0]],
                             invalid_dict['error'][1])

        valid_data_dicts = [
            {'identification': 'john',
             'password': 'pass'},
            {'identification': 'john@example.com',
             'password': 'pass'}
        ]

        for valid_dict in valid_data_dicts:
            form = forms.AuthenticationForm(valid_dict)
            self.failUnless(form.is_valid())

    def test_authentication_form_email(self):
        """
        Test that the signin form has a different label is
        ``ACCOUNTS_WITHOUT_USERNAME`` is set to ``True``

        """
        defaults.ACCOUNTS_WITHOUT_USERNAMES = True

        form = forms.AuthenticationForm(data={'identification': "john",
                                              'password': "test"})

        correct_label = _(u"Email address")
        self.assertEqual(form.fields['identification'].label,
                         correct_label)

        # Restore default settings
        defaults.ACCOUNTS_WITHOUT_USERNAMES = False

class RegistrationFormOnlyEmailTests(AccountsTestCase):
    """
    Test the :class:`RegistrationFormOnlyEmail`.

    This is the same form as :class:`RegistrationForm` but doesn't require an
    username for a successfull signup.

    """
    fixtures = ['test']

    def test_registration_form_only_email(self):
        """
        Test that the form has no username field. And that the username is
        generated in the save method

        """
        valid_data = {'email': 'johndoe@example.com',
                      'password1': 'pass',
                      'password2': 'pass'}

        form = forms.RegistrationFormOnlyEmail(data=valid_data)

        # Should have no username field
        self.failIf(form.fields.get('username', False))

        # Form should be valid.
        self.failUnless(form.is_valid())

        # Creates an unique username
        user = form.save()

        self.failUnless(len(user.username), 5)

class EmailFormTests(AccountsTestCase):
    """ Test the ``EmailForm`` """
    fixtures = ['test']

    def test_email_form(self):
        user = get_user_model().objects.get(pk=1)
        invalid_data_dicts = [
            # No change in e-mail address
            {'data': {'email': 'john@example.com'},
             'error': ('email', [_(u"You're already known under this email address.")])},
            # An e-mail address used by another
            {'data': {'email': 'jane@example.com'},
             'error': ('email', [_(u'This email address is already in use. Please supply a different email address.')])},
        ]
        for invalid_dict in invalid_data_dicts:
            form = forms.EmailForm(user, data=invalid_dict['data'])
            self.failIf(form.is_valid())
            self.assertEqual(form.errors[invalid_dict['error'][0]],
                             invalid_dict['error'][1])

        # Test a valid post
        form = forms.EmailForm(user,
                                     data={'email': 'john.doe@example.com'})
        self.failUnless(form.is_valid())

    def test_form_init(self):
        """ The form must be initialized with a ``User`` instance. """
        self.assertRaises(TypeError, forms.EmailForm, None)
