from django.conf import settings

BOOTSTRAP_GRID_COLUMNS = getattr(settings, 'BOOTSTRAP_GRID_COLUMNS', 12)