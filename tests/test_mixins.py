# -*- coding: utf-8 -*-
""" Manifest View Mixin Tests
"""

from django.core import mail
from django.core.exceptions import ImproperlyConfigured
from django.urls import reverse

from manifest import messages
from manifest.views import EmailChangeView
from tests import data_dicts
from tests.base import ManifestTestCase


class MessageMixinTests(ManifestTestCase):
    """Tests for Manifest view mixins.
    """

    form_data = data_dicts.LOGIN_FORM["valid"][0]

    def test_message_mixin_success(self):
        """Response should contain ``messages``.
        """
        with self.defaults(MANIFEST_USE_MESSAGES=True):
            response = self.client.get(reverse("auth_logout"))
            response_messages = list(response.context["messages"])
            self.assertEqual(len(response_messages), 1)
            self.assertEqual(
                str(response_messages[0]), messages.AUTH_LOGOUT_SUCCESS
            )

    def test_message_mixin_error(self):
        """Response should contain ``messages``.
        """
        with self.defaults(MANIFEST_USE_MESSAGES=True):
            response = self.client.get(
                reverse(
                    "auth_activate",
                    kwargs={"username": "alice", "token": "fake"},
                )
            )
            response_messages = list(response.context["messages"])
            self.assertNotEqual(len(response_messages), 0)
            self.assertEqual(
                str(response_messages[0]), messages.AUTH_ACTIVATE_ERROR
            )


class SendMailMixinTests(ManifestTestCase):
    """Tests for Manifest view mixins.
    """

    form_data = data_dicts.LOGIN_FORM["valid"][0]

    def test_send_mail_mixin_subject(self):
        """Should raise ``ImproperlyConfigured``.
        """
        # pylint: disable=bad-continuation
        with self.assertRaisesRegex(
            ImproperlyConfigured, "No template name for subject."
        ):
            view = EmailChangeView(
                email_subject_template_name=None,
                email_message_template_name="dummy",
            )
            view.create_email(None, None)

    def test_send_mail_mixin_message(self):
        """Should raise ``ImproperlyConfigured``.
        """
        # pylint: disable=bad-continuation
        with self.assertRaisesRegex(
            ImproperlyConfigured, "No template name for message."
        ):
            view = EmailChangeView(
                email_subject_template_name="dummy",
                email_message_template_name=None,
            )
            view.create_email(None, None)

    def test_send_mail_mixin_html(self):
        """Should send 2 emails.
        """
        self.client.login(
            username=self.form_data["identification"],
            password=self.form_data["password"],
        )
        response = self.client.post(
            reverse("test_send_mail_mixin_html"),
            data={"email": "email@example.com"},
        )
        self.assertEqual(len(mail.outbox), 2)
        self.assertTemplateUsed(
            response, "manifest/emails/confirmation_email_message_new.txt"
        )
