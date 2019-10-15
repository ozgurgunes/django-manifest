# -*- coding: utf-8 -*-
""" Manifest Clean Expired Users Command
"""

try:
    from django.core.management.base import NoArgsCommand as BaseCommand
except ImportError:
    from django.core.management.base import BaseCommand

from django.contrib.auth import get_user_model

USER_MODEL = get_user_model()


class Command(BaseCommand):
    """
    Search for users that still haven't verified their email after
    ``MANIFEST_ACTIVATION_DAYS`` and delete them.

    """

    help = "Deletes expired users."

    # pylint: disable=W0612,W0613
    def handle(self, *args, **kwargs):
        USER_MODEL.objects.delete_expired_users()  # noqa: F841
