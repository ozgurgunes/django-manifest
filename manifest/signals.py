# -*- coding: utf-8 -*-
""" Manifest Signals
"""

from django.dispatch import Signal

REGISTRATION_COMPLETE = Signal(providing_args=["user", "request"])
ACTIVATION_COMPLETE = Signal(providing_args=["user"])
CINFIRMATION_COMPLETE = Signal(providing_args=["user"])
PASSWORD_RESET_COMPLETE = Signal(providing_args=["user"])
