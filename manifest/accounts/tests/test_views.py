# -*- coding: utf-8 -*-
from django.conf import settings
from django.core import mail
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm

from manifest.accounts import forms
from manifest.accounts import defaults
from manifest.accounts.tests.base import AccountsTestCase

class AccountsViewsTests(AccountsTestCase):
    """ Test the account views """
    fixtures = ['test']

    def test_valid_activation(self):
        """ A ``GET`` to the activation view """
        # First, register an account.
        self.client.post(reverse('accounts_register'),
                         data={'username': 'alice',
                               'email': 'alice@example.com',
                               'password1': 'pass',
                               'password2': 'pass',
                               'tos': 'on'})
        user = get_user_model().objects.get(email='alice@example.com')
        response = self.client.get(reverse('accounts_activate',
                                           kwargs={'username': user.username,
                                                   'activation_key': user.activation_key}))
        self.assertRedirects(response,
                             reverse('accounts_profile_detail', kwargs={'username': user.username}))

        user = get_user_model().objects.get(email='alice@example.com')
        self.failUnless(user.is_active)

    def test_invalid_activation(self):
        """
        A ``GET`` to the activation view with a wrong ``activation_key``.

        """
        response = self.client.get(reverse('accounts_activate',
                                           kwargs={'username': 'john',
                                                   'activation_key': 'fake'}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                                'accounts/activate_fail.html')

    def test_valid_confirmation(self):
        """ A ``GET`` to the verification view """
        # First, try to change an email.
        user = get_user_model().objects.get(pk=1)
        user.change_email('johnie@example.com')

        response = self.client.get(reverse('accounts_email_confirm',
                                           kwargs={'username': user.username,
                                                   'confirmation_key': user.email_confirmation_key}))

        self.assertRedirects(response,
                             reverse('accounts_email_change_complete', kwargs={'username': user.username}))

    def test_invalid_confirmation(self):
        """
        A ``GET`` to the verification view with an invalid verification key.

        """
        response = self.client.get(reverse('accounts_email_confirm',
                                           kwargs={'username': 'john',
                                                   'confirmation_key': 'WRONG'}))
        self.assertTemplateUsed(response,
                                'accounts/email_change_fail.html')

    def test_disabled_view(self):
        """ A ``GET`` to the ``disabled`` view """
        response = self.client.get(reverse('accounts_disabled',
                                           kwargs={'username': 'john'}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                                'accounts/disabled.html')

    def test_register_view(self):
        """ A ``GET`` to the ``register`` view """
        response = self.client.get(reverse('accounts_register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                                'accounts/register.html')

        # Check that the correct form is used.
        self.failUnless(isinstance(response.context['form'],
                                   forms.RegistrationForm))

        # Now check that a different form is used when
        # ``ACCOUNTS_WITHOUT_USERNAMES`` setting is set to ``True``
        defaults.ACCOUNTS_WITHOUT_USERNAMES = True

        response = self.client.get(reverse('accounts_register'))
        self.failUnless(isinstance(response.context['form'],
                                   forms.RegistrationFormOnlyEmail))

        # Back to default
        defaults.ACCOUNTS_WITHOUT_USERNAMES = False

    def test_register_view_redirect(self):
        """ Check that an authenticated user shouldn't register. """
        # User should be signed in
        self.failUnless(self.client.login(username='john', password='pass'))
        # Post a new, valid register
        response = self.client.post(reverse('accounts_register'),
                                    data={'username': 'alice',
                                          'email': 'alice@example.com',
                                          'password1': 'blueberry',
                                          'password2': 'blueberry',
                                          'tos': 'on'})

        # And should now be redirected to settings
        self.assertRedirects(response, reverse('accounts_settings'))

    def test_register_view_success(self):
        """
        After a ``POST`` to the ``register`` view a new user should be created,
        the user should be logged in and redirected to the register success page.

        """
        response = self.client.post(reverse('accounts_register'),
                                    data={'username': 'alice',
                                          'email': 'alice@example.com',
                                          'password1': 'blueberry',
                                          'password2': 'blueberry',
                                          'tos': 'on'})

        # Check for redirect.
        self.assertRedirects(response,
                             reverse('accounts_register_complete', kwargs={'username': 'alice'}))

        # Check for new user.
        self.assertEqual(get_user_model().objects.filter(email__iexact='alice@example.com').count(), 1)

    def test_login_view(self):
        """ A ``GET`` to the login view should render the correct form """
        response = self.client.get(reverse('accounts_login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                                'accounts/login.html')

    def test_login_view_remember_me_on(self):
        """
        A ``POST`` to the login with tells it to remember the user for
        ``REMEMBER_ME_DAYS``.

        """
        response = self.client.post(reverse('accounts_login'),
                                    data={'identification': 'john@example.com',
                                          'password': 'pass',
                                          'remember_me': True})
        self.assertEqual(self.client.session.get_expiry_age(),
                         defaults.ACCOUNTS_REMEMBER_ME_DAYS[1] * 3600 * 24)

    def test_login_view_remember_off(self):
        """
        A ``POST`` to the login view of which the user doesn't want to be
        remembered.

        """
        response = self.client.post(reverse('accounts_login'),
                                    data={'identification': 'john@example.com',
                                          'password': 'pass'})

        self.failUnless(self.client.session.get_expire_at_browser_close())

    def test_login_view_inactive(self):
        """ A ``POST`` from a inactive user """
        user = get_user_model().objects.get(email='john@example.com')
        user.is_active = False
        user.save()

        response = self.client.post(reverse('accounts_login'),
                                    data={'identification': 'john@example.com',
                                          'password': 'pass'})

        self.assertRedirects(response,
                             reverse('accounts_disabled',
                                     kwargs={'username': user.username}))

    def test_login_view_success(self):
        """
        A valid ``POST`` to the login view should redirect the user to it's
        own profile page if no ``next`` value is supplied. Else it should
        redirect to ``next``.

        """
        response = self.client.post(reverse('accounts_login'),
                                    data={'identification': 'john@example.com',
                                          'password': 'pass'})

        self.assertRedirects(response, reverse('accounts_profile_detail',
                                               kwargs={'username': 'john'}))

        # Redirect to supplied ``next`` value.
        response = self.client.post(reverse('accounts_login'),
                                    data={'identification': 'john@example.com',
                                          'password': 'pass',
                                          'next': '/'})
        self.assertRedirects(response, '/')

    def test_logout_view(self):
        """ A ``GET`` to the logout view """
        response = self.client.get(reverse('accounts_logout'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                                'accounts/logout.html')

    def test_change_email_view(self):
        """ A ``GET`` to the change e-mail view. """
        response = self.client.get(reverse('accounts_email_change'))

        # Anonymous user should not be able to view the profile page
        self.assertEqual(response.status_code, 302)

        # Login
        client = self.client.login(username='john', password='pass')
        response = self.client.get(reverse('accounts_email_change'))

        self.assertEqual(response.status_code, 200)

        # Check that the correct form is used.
        self.failUnless(isinstance(response.context['form'],
                                   forms.EmailForm))

        self.assertTemplateUsed(response,
                                'accounts/email_change_form.html')

    def test_change_email_success(self):
        """ A ``POST`` with a valid e-mail address """
        self.client.login(username='john', password='pass')
        response = self.client.post(reverse('accounts_email_change'),
                                    data={'email': 'john_new@example.com'})

        self.assertRedirects(response,
                             reverse('accounts_email_change_done',
                                     kwargs={'username': 'john'}))

    def test_change_password_view(self):
        """ A ``GET`` to the change password view """
        self.client.login(username='john', password='pass')
        response = self.client.get(reverse('accounts_password_change'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/password_change_form.html')
        self.failUnless(response.context['form'],
                        PasswordChangeForm)

    def test_change_password_view_success(self):
        """ A valid ``POST`` to the password change view """
        self.client.login(username='john', password='pass')

        new_password = 'newpass'
        response = self.client.post(reverse('accounts_password_change'),
                                    data={'new_password1': new_password,
                                          'new_password2': 'newpass',
                                          'old_password': 'pass'})

        self.assertRedirects(response, reverse('accounts_password_change_done',
                                               kwargs={'username': 'john'}))

        # Check that the new password is set.
        john = get_user_model().objects.get(username='john')
        self.failUnless(john.check_password(new_password))

    def test_profile_detail_view(self):
        """ A ``GET`` to the detailed view of a user """
        response = self.client.get(reverse('accounts_profile_detail',
                                           kwargs={'username': 'john'}))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/profile_detail.html')

    def test_profile_edit_view(self):
        """ A ``GET`` to the edit view of a users account """
        self.client.login(username='john', password='pass')
        response = self.client.get(reverse('accounts_update'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/profile_form.html')
        self.failUnless(response.context['form'], forms.ProfileForm)

    def test_profile_list_view(self):
        """ A ``GET`` to the list view of a user """

        # A profile list should be shown.
        defaults.ACCOUNTS_DISABLE_PROFILE_LIST = False
        response = self.client.get(reverse('accounts_profile_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/profile_list.html')

        # Profile list is disabled.
        defaults.ACCOUNTS_DISABLE_PROFILE_LIST = True
        response = self.client.get(reverse('accounts_profile_list'))
        self.assertEqual(response.status_code, 404)