# -*- coding: utf-8 -*-
""" Manifest Admin
"""

# from django.contrib import admin
# from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


class UserAdmin(BaseUserAdmin):
    pass


# admin.site.unregister(get_user_model())
# admin.site.register(get_user_model(), UserAdmin)
