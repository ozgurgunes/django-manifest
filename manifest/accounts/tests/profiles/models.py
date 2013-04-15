from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model

from manifest.accounts.models import ProfileBase

import datetime

class Profile(ProfileBase):
    pass
