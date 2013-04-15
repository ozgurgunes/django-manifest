# -*- coding: utf-8 -*-
from django.core.management.base import NoArgsCommand

from django.contrib.auth import get_user_model


class Command(NoArgsCommand):
    """
    Search for users that still haven't verified their email after
    ``ACCOUNTS_ACTIVATION_DAYS`` and delete them.

    """
    help = 'Deletes expired users.'
    def handle_noargs(self, **options):
        users = get_user_model().objects.delete_expired_users()
