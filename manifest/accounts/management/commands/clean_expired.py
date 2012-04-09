from django.core.management.base import NoArgsCommand

from manifest.accounts.models import Account

class Command(NoArgsCommand):
    """
    Search for users that still haven't verified their email after
    ``ACCOUNTS_ACTIVATION_DAYS`` and delete them.

    """
    help = 'Deletes expired users.'
    def handle_noargs(self, **options):
        users = Account.objects.delete_expired_users()
