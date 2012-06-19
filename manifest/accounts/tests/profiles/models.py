from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

from manifest.accounts.models import ProfileBase

import datetime

class Profile(ProfileBase):
    pass
