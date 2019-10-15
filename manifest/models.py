# -*- coding: utf-8 -*-
""" Manifest Models
"""

import datetime

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.files.storage import default_storage
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from dateutil.relativedelta import relativedelta
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from pytz import common_timezones

from manifest import defaults
from manifest.managers import UserManager
from manifest.utils import generate_sha1, get_gravatar, get_image_path


class AccountActivationMixin(models.Model):
    """
    A mixin that adds the field and methods necessary to support
    account activation.
    """

    activation_key = models.CharField(
        _("Activation key"), max_length=40, blank=True
    )

    class Meta:
        abstract = True

    def activation_key_expired(self):
        """
        Checks if activation key is expired.

        Returns ``True`` when the ``activation_key`` of the user is expired
        or ``False`` if the key is still valid.

        The key is expired when it's set to the value defined in
        ``MANIFEST_ACTIVATED_LABEL`` or ``activation_key_created`` is beyond the
        amount of days defined in ``MANIFEST_ACTIVATION_DAYS``.

        """
        expiration_days = datetime.timedelta(
            days=defaults.MANIFEST_ACTIVATION_DAYS
        )
        expiration_date = self.date_joined + expiration_days
        if self.activation_key == defaults.MANIFEST_ACTIVATED_LABEL:
            return True
        if timezone.now() >= expiration_date:
            return True
        return False


class EmailConfirmationMixin(models.Model):
    """
    A mixin that adds the field and methods necessary to support
    e-mail address confirmation.
    """

    email_unconfirmed = models.EmailField(
        _("Unconfirmed email address"),
        blank=True,
        help_text=_(
            "Temporary email address when the "
            "user requests an email change."
        ),
    )

    email_confirmation_key = models.CharField(
        _("Unconfirmed email " "verification key"), max_length=40, blank=True
    )

    email_confirmation_key_created = models.DateTimeField(
        _("Creation date " "of email confirmation key"), blank=True, null=True
    )

    class Meta:
        abstract = True

    def change_email(self, email):
        """
        Changes the email address for a user.

        A user needs to verify this new email address before it becomes
        active. By storing the new email address in a temporary field
        -- ``temporary_email`` -- we are able to set this email address
        after the user has verified it by clicking on the verification URI
        in the email. This email gets send out by ``send_verification_email``.

        :param email:
            The new email address that the user wants to use.

        """
        self.email_unconfirmed = email

        key = generate_sha1(self.username)
        self.email_confirmation_key = key[1]
        self.email_confirmation_key_created = timezone.now()
        self.save()

        return self


class UserProfileMixin(models.Model):
    """
    Base model needed for extra profile functionality

    """

    GENDER_CHOICES = (("F", _("Female")), ("M", _("Male")))

    gender = models.CharField(
        _("Gender"),
        choices=GENDER_CHOICES,
        max_length=1,
        blank=True,
        null=True,
    )
    birth_date = models.DateField(_("Birth date"), blank=True, null=True)
    picture = models.ImageField(
        _("Picture"), blank=True, null=True, upload_to=get_image_path
    )
    mugshot = ImageSpecField(
        source="picture",
        processors=[
            ResizeToFill(
                defaults.MANIFEST_AVATAR_SIZE, defaults.MANIFEST_AVATAR_SIZE
            )
        ],
        format="JPEG",
        options={"quality": 80},
    )

    class Meta:
        abstract = True

    def get_absolute_url(self):
        return ("user_detail", None, {"username": self.username})

    # pylint: disable=arguments-differ
    def save(self, *args, force_insert=False, force_update=False, **kwargs):
        try:
            old_obj = self.__class__.objects.get(pk=self.pk)
            # pylint: disable=bad-continuation
            if (
                old_obj.picture
                and self.picture
                # pylint: disable=no-member
                and old_obj.picture.path != self.picture.path
            ):
                path = old_obj.picture.path
                default_storage.delete(path)
        except self.__class__.DoesNotExist:
            pass
        super().save(force_insert, force_update, *args, **kwargs)

    @property
    def avatar(self):
        return self.get_avatar()

    # @property
    # def mugshot(self):
    #     """docstring for mugshot"""
    #     return get_thumbnail(self.avatar, '256x256', crop='center').url

    @property
    def age(self):
        today = datetime.date.today()
        if self.birth_date:
            return "%s" % relativedelta(today, self.birth_date).years
        return None

    def get_avatar(self):
        """
        Returns a profile picture for user. The picture could be
        an uploaded image by user, Gravatar or any other set in defaults.

        """

        # First check for the mugshot, return that if exist.
        if self.mugshot:
            # pylint: disable=no-member
            return self.mugshot.url
        # Use Gravatar if it is set as default.
        if defaults.MANIFEST_AVATAR_DEFAULT == "gravatar":
            return get_gravatar(self.email)
        # Gravatar is not used, so return default image.
        return defaults.MANIFEST_AVATAR_DEFAULT

    def get_full_name_or_username(self):
        """
        Returns the full name of the user, or if none is supplied will return
        the username.

        :return:
            ``String`` containing the full name of the user. If no name is
            supplied it will return the username.

        """
        if self.first_name or self.last_name:
            # We will return this as translated string. Maybe there are some
            # countries that first display the last name.
            name = _("%(first_name)s %(last_name)s") % {
                "first_name": self.first_name,
                "last_name": self.last_name,
            }
        else:
            name = "%(username)s" % {"username": self.username}
        return name.strip()

    def get_short_name_or_username(self):
        """
        Returns the short name (ex: John S.) of the user,
        if no name is supplied then returns the username.

        :return:
            ``String`` containing the short name or username of the user.

        """
        if self.first_name or self.last_name:
            name = "%(first_name)s %(last_name)s." % {
                "first_name": self.first_name,
                "last_name": self.last_name[0],
            }
        else:
            name = "%(username)s" % {"username": self.username}
        return name.strip()


class UserLocaleMixin(models.Model):
    """
    A mixin that adds the field and methods necessary to support
    i18n & L10n for UI.
    """

    TIMEZONE_CHOICES = ([tz, tz.replace("_", " ")] for tz in common_timezones)

    timezone = models.CharField(
        _("Timezone"),
        max_length=64,
        null=False,
        blank=False,
        choices=TIMEZONE_CHOICES,
        default=defaults.MANIFEST_TIME_ZONE,
    )

    locale = models.CharField(
        _("Locale"),
        max_length=10,
        null=False,
        blank=False,
        choices=settings.LANGUAGES,
        default=defaults.MANIFEST_LANGUAGE_CODE,
    )

    class Meta:
        abstract = True


# pylint: disable=bad-continuation
class BaseUser(
    AccountActivationMixin,
    EmailConfirmationMixin,
    UserProfileMixin,
    UserLocaleMixin,
):
    """
    Custom user model base which stores all the necessary information
    to have a fully functional user implementation on your Django website.
    """

    class Meta:
        abstract = True


# pylint: disable=too-many-ancestors
class User(AbstractUser, BaseUser):

    objects = UserManager()

    class Meta:
        swappable = "AUTH_USER_MODEL"
        ordering = ["-date_joined"]
