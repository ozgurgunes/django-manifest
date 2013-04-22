# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import ugettext as _

from manifest.accounts import defaults


class UserAdmin(BaseUserAdmin):
    pass

#admin.site.unregister(get_user_model())
admin.site.register(get_user_model(), UserAdmin)
