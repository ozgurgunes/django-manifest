# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import ugettext as _

from manifest.accounts.utils import get_profile_model
from manifest.accounts.forms import get_profile_model
from manifest.accounts import settings as accounts_settings


class UserAdmin(BaseUserAdmin):
    pass

#admin.site.unregister(get_user_model())
admin.site.register(get_user_model(), UserAdmin)
admin.site.register(get_profile_model())
