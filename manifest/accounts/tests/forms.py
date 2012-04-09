from django.test import TestCase
from django.contrib.auth.models import User

from manifest.accounts import forms
from manifest.accounts import settings as accounts_settings

class RegistrationFormTests(TestCase):
    """ Test the register form. """
    fixtures = ['users']

    def test_registration_form(self):
        """
        Test that the ``RegistrationForm`` checks for unique usernames and unique
        e-mail addresses.

        """
        invalid_data_dicts = [
            # Non-alphanumeric username.
            {'data': {'username': 'foo@bar',
                      'email': 'foo@example.com',
                      'password': 'foo',
                      'password2': 'foo',
                      'tos': 'on'},
             'error': ('username', [u'Username must contain only letters, numbers and underscores.'])},
            # Password is not the same
            {'data': {'username': 'katy',
                      'email': 'katy@newexample.com',
                      'password1': 'foo',
                      'password2': 'foo2',
                      'tos': 'on'},
             'error': ('__all__', [u'The two password fields didn\'t match.'])},

            # Already taken username
            {'data': {'username': 'john',
                      'email': 'john@newexample.com',
                      'password1': 'foo',
                      'password2': 'foo',
                      'tos': 'on'},
             'error': ('username', [u'This username is already taken.'])},

            # Forbidden username
            {'data': {'username': 'SignUp',
                      'email': 'foo@example.com',
                      'password': 'foo',
                      'password2': 'foo2',
                      'tos': 'on'},
             'error': ('username', [u'This username is not allowed.'])},

            # Already taken email
            {'data': {'username': 'alice',
                      'email': 'john@example.com',
                      'password': 'foo',
                      'password2': 'foo',
                      'tos': 'on'},
             'error': ('email', [u'This email is already in use. Please supply a different email.'])},
        ]

        for invalid_dict in invalid_data_dicts:
            form = forms.RegistrationForm(data=invalid_dict['data'])
            self.failIf(form.is_valid())
            self.assertEqual(form.errors[invalid_dict['error'][0]],
                             invalid_dict['error'][1])


        # And finally, a valid form.
        form = forms.RegistrationForm(data={'username': 'foobla',
                                      'email': 'foo@example.com',
                                      'password1': 'foo',
                                      'password2': 'foo',
                                      'tos': 'on'})

        self.failUnless(form.is_valid())

class AuthenticationFormTests(TestCase):
    """ Test the ``AuthenticationForm`` """

    fixtures = ['users',]

    def test_login_form(self):
        """
        Check that the ``SigninForm`` requires both identification and password

        """
        invalid_data_dicts = [
            {'data': {'identification': '',
                      'password': 'inhalefish'},
             'error': ('identification', [u'Either supply us with your email or username.'])},
            {'data': {'identification': 'john',
                      'password': 'inhalefish'},
             'error': ('__all__', [u'Please enter a correct username or email and password. Note that both fields are case-sensitive.'])}
        ]

        for invalid_dict in invalid_data_dicts:
            form = forms.AuthenticationForm(data=invalid_dict['data'])
            self.failIf(form.is_valid())
            self.assertEqual(form.errors[invalid_dict['error'][0]],
                             invalid_dict['error'][1])

        valid_data_dicts = [
            {'identification': 'john',
             'password': 'blowfish'},
            {'identification': 'john@example.com',
             'password': 'blowfish'}
        ]

        for valid_dict in valid_data_dicts:
            form = forms.AuthenticationForm(valid_dict)
            self.failUnless(form.is_valid())

    def test_login_form_email(self):
        """
        Test that the login form has a different label is
        ``ACCOUNTS_WITHOUT_USERNAME`` is set to ``True``

        """
        accounts_settings.ACCOUNTS_WITHOUT_USERNAMES = True

        form = forms.AuthenticationForm(data={'identification': "john",
                                              'password': "blowfish"})

        correct_label = "Email"
        self.assertEqual(form.fields['identification'].label,
                         correct_label)

        # Restore default settings
        accounts_settings.ACCOUNTS_WITHOUT_USERNAMES = False

class RegistrationFormOnlyEmailTests(TestCase):
    """
    Test the :class:`RegistrationFormOnlyEmail`.

    This is the same form as :class:`RegistrationForm` but doesn't require an
    username for a successfull register.

    """
    fixtures = ['users']

    def test_registration_form_only_email(self):
        """
        Test that the form has no username field. And that the username is
        generated in the save method

        """
        valid_data = {'email': 'hans@gretel.com',
                      'password1': 'blowfish',
                      'password2': 'blowfish'}

        form = forms.RegistrationFormOnlyEmail(data=valid_data)

        # Should have no username field
        self.failIf(form.fields.get('username', False))

        # Form should be valid.
        self.failUnless(form.is_valid())

        # Creates an unique username
        user = form.save()

        self.failUnless(len(user.username), 5)

class EmailFormTests(TestCase):
    """ Test the ``EmailForm`` """
    fixtures = ['users']

    def test_email_form(self):
        user = User.objects.get(pk=1)
        invalid_data_dicts = [
            # No change in e-mail address
            {'data': {'email': 'john@example.com'},
             'error': ('email', [u'You\'re already known under this email.'])},
            # An e-mail address used by another
            {'data': {'email': 'jane@example.com'},
             'error': ('email', [u'This email is already in use. Please supply a different email.'])},
        ]
        for invalid_dict in invalid_data_dicts:
            form = forms.EmailForm(user, data=invalid_dict['data'])
            self.failIf(form.is_valid())
            self.assertEqual(form.errors[invalid_dict['error'][0]],
                             invalid_dict['error'][1])

        # Test a valid post
        form = forms.EmailForm(user,
                                     data={'email': 'john@newexample.com'})
        self.failUnless(form.is_valid())

    def test_form_init(self):
        """ The form must be initialized with a ``User`` instance. """
        self.assertRaises(TypeError, forms.EmailForm, None)

class AccountFormTest(TestCase):
    """ Test the ``AccountForm`` """
    pass
