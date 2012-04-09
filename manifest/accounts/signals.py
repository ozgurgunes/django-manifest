from django.dispatch import Signal

registration_complete = Signal(providing_args=['user', 'request',])
activation_complete = Signal(providing_args=['user',])
confirmation_complete = Signal(providing_args=['user',])
password_complete = Signal(providing_args=['user',])
