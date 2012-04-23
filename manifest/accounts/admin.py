# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

from manifest.accounts.models import Account
from manifest.accounts.utils import get_profile_model

class AccountInline(admin.StackedInline):
    model = Account
    max_num = 1

class AccountAdmin(UserAdmin):
    inlines = [AccountInline, ]
    list_display = ('username', 'email', 'first_name', 'last_name', 
                    'is_staff', 'date_joined')

admin.site.unregister(User)
admin.site.register(User, AccountAdmin)
admin.site.register(get_profile_model())
