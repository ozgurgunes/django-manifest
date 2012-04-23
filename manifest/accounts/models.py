# -*- coding: utf8 -*-
import datetime

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _
from django.core.mail import send_mail
from django.core.files.storage import default_storage
from django.template.loader import render_to_string

from timezones.fields import TimeZoneField

from manifest.accounts.managers import AccountsManager, ProfileBaseManager
from manifest.accounts.utils import get_gravatar, generate_sha1, get_protocol, get_datetime_now
from manifest.accounts import settings as accounts_settings


class Account(models.Model):
    """
    Accounts model which stores all the necessary information to have a full
    functional user implementation on your Django website.

    """

    user = models.OneToOneField(User, verbose_name=_('user'), related_name='account')

    activation_key = models.CharField(_('activation key'), max_length=40, blank=True)

    email_unconfirmed = models.EmailField(_('unconfirmed email address'), blank=True,
                            help_text=_('Temporary email address when the user requests an email change.'))

    email_confirmation_key = models.CharField(_('unconfirmed email verification key'), 
                                        max_length=40, blank=True)

    email_confirmation_key_created = models.DateTimeField(_('creation date of email confirmation key'),
                                        blank=True, null=True)

    objects = AccountsManager()

    class Meta:
        verbose_name = _('account')
        verbose_name_plural = _('accounts')

    def __unicode__(self):
        return 'account of %s' % self.user.username

    def change_email(self, email):
        """
        Changes the email address for a user.

        A user needs to verify this new email address before it becomes
        active. By storing the new email address in a temporary field --
        ``temporary_email`` -- we are able to set this email address after the
        user has verified it by clicking on the verification URI in the email.
        This email gets send out by ``send_verification_email``.

        :param email:
            The new email address that the user wants to use.

        """
        self.email_unconfirmed = email

        salt, hash = generate_sha1(self.user.username)
        self.email_confirmation_key = hash
        self.email_confirmation_key_created = get_datetime_now()
        self.save()

        # Send email for activation
        self.send_confirmation_email()

    def send_confirmation_email(self):
        """
        Sends an email to confirm the new email address.

        This method sends out two emails. One to the new email address that
        contains the ``email_confirmation_key`` which is used to verify this
        this email address with :func:`AccountsUser.objects.confirm_email`.

        The other email is to the old email address to let the user know that
        a request is made to change this email address.

        """
        context= {'user': self.user,
                  'without_usernames': accounts_settings.ACCOUNTS_WITHOUT_USERNAMES,
                  'new_email': self.email_unconfirmed,
                  'protocol': get_protocol(),
                  'confirmation_key': self.email_confirmation_key,
                  'site': Site.objects.get_current()}


        # Email to the old address
        subject_old = render_to_string('accounts/emails/confirmation_email_subject_old.txt',
                                       context)
        subject_old = ''.join(subject_old.splitlines())

        message_old = render_to_string('accounts/emails/confirmation_email_message_old.txt',
                                       context)

        send_mail(subject_old,
                  message_old,
                  settings.DEFAULT_FROM_EMAIL,
                  [self.user.email])

        # Email to the new address
        subject_new = render_to_string('accounts/emails/confirmation_email_subject_new.txt',
                                       context)
        subject_new = ''.join(subject_new.splitlines())

        message_new = render_to_string('accounts/emails/confirmation_email_message_new.txt',
                                       context)

        send_mail(subject_new,
                  message_new,
                  settings.DEFAULT_FROM_EMAIL,
                  [self.email_unconfirmed,])

    def activation_key_expired(self):
        """
        Checks if activation key is expired.

        Returns ``True`` when the ``activation_key`` of the user is expired and
        ``False`` if the key is still valid.

        The key is expired when it's set to the value defined in
        ``ACCOUNTS_ACTIVATED`` or ``activation_key_created`` is beyond the
        amount of days defined in ``ACCOUNTS_ACTIVATION_DAYS``.

        """
        expiration_days = datetime.timedelta(days=accounts_settings.ACCOUNTS_ACTIVATION_DAYS)
        expiration_date = self.user.date_joined + expiration_days
        if self.activation_key == accounts_settings.ACCOUNTS_ACTIVATED:
            return True
        if get_datetime_now() >= expiration_date:
            return True
        return False

    def send_activation_email(self):
        """
        Sends a activation email to the user.

        This email is send when the user wants to activate their newly created
        user.

        """
        context= {'user': self.user,
                  'without_usernames': accounts_settings.ACCOUNTS_WITHOUT_USERNAMES,
                  'protocol': get_protocol(),
                  'activation_days': accounts_settings.ACCOUNTS_ACTIVATION_DAYS,
                  'activation_key': self.activation_key,
                  'site': Site.objects.get_current()}

        subject = render_to_string('accounts/emails/activation_email_subject.txt',
                                   context)
        subject = ''.join(subject.splitlines())

        message = render_to_string('accounts/emails/activation_email_message.txt',
                                   context)
        send_mail(subject,
                  message,
                  settings.DEFAULT_FROM_EMAIL,
                  [self.user.email,])


if 'social_auth' in settings.INSTALLED_APPS:
    from social_auth.signals import socialauth_registered

    def create_user_account(sender, user, *args, **kwargs):
        account = Account.objects.create_account(user=user)
        user = Account.objects.activate_user(user.username, account.activation_key)
        
    socialauth_registered.connect(create_user_account, sender=None)

"""
User profile base class

"""
def upload_to_picture(instance, filename):
    """
    Uploads a picture for a user to the ``ACCOUNTS_GRAVATAR_PATH`` and saving it
    under unique hash for the image. This is for privacy reasons so others
    can't just browse through the picture directory.

    """
    extension = filename.split('.')[-1].lower()
    salt, hash = generate_sha1(instance.id)
    return '%(path)s/%(hash)s.%(extension)s' % {'path': getattr(accounts_settings, 
                                                        'ACCOUNTS_GRAVATAR_PATH','%s/%s' % (
                                                            str(instance._meta.app_label), 
                                                            str(instance._meta.module_name)
                                                            )
                                                        ),
                                               'hash': hash[:10],
                                               'extension': extension
                                               }

class ProfileBase(models.Model):
    """ Base model needed for extra profile functionality """

    GENDER_CHOICES = (
        ('F', _('Female')),
        ('M', _('Male')),
    )
    
    user = models.OneToOneField(User, unique=True, verbose_name=_('user'), related_name='profile')

    birth_date = models.DateField(_('birth date'), blank=True, null=True)
    gender = models.CharField(_('gender'), choices=GENDER_CHOICES, max_length=1, blank=True, null=True)
    picture = models.ImageField(_('picture'), blank=True, upload_to=upload_to_picture)
    timezone = TimeZoneField(_("timezone"))
    locale = models.CharField(_("locale"), max_length = 10,
                                    choices = settings.LANGUAGES,
                                    default = settings.LANGUAGE_CODE)

    objects = ProfileBaseManager()


    class Meta:
        """
        Meta options making the model abstract.

        The model is ``abstract`` because it only supplies basic functionality
        to a more custom defined model that extends it. This way there is not
        another join needed.

        """
        abstract = True

    def __unicode__(self):
        return 'Profile of %(username)s' % {'username': self.user.username}

    @models.permalink
    def get_absolute_url(self):
        return ('accounts_profile_detail', None, { 'username': self.user.username })

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        try:
            old_obj = self.__class__.objects.get(pk=self.pk)
            if old_obj.picture.path != self.picture.path:
                path = old_obj.picture.path
                default_storage.delete(path)
        except:
            pass
        super(ProfileBase, self).save(force_insert, force_update, *args, **kwargs)

    @property
    def avatar(self):
        return self.get_picture_url()

    @property
    def age(self):
        TODAY = datetime.date.today()
        if self.birth_date:
            return u"%s" % relativedelta.relativedelta(TODAY, self.birth_date).years
        else:
            return None

    def get_picture_url(self):
        """
        Returns the image containing the picture for the user.

        The picture can be a uploaded image or a Gravatar.

        Gravatar functionality will only be used when
        ``ACCOUNTS_GRAVATAR_PICTURE`` is set to ``True``.

        :return:
            ``None`` when Gravatar is not used and no default image is supplied
            by ``ACCOUNTS_GRAVATAR_DEFAULT``.

        """
        # First check for a picture and if any return that.
        if self.picture:
            return self.picture.url

        # Use Gravatar if the user wants to.
        if accounts_settings.ACCOUNTS_GRAVATAR_PICTURE:
            return get_gravatar(self.user.email,
                                accounts_settings.ACCOUNTS_GRAVATAR_SIZE,
                                accounts_settings.ACCOUNTS_GRAVATAR_DEFAULT)

        # Gravatar not used, check for a default image.
        else:
            if accounts_settings.ACCOUNTS_GRAVATAR_DEFAULT not in ['404', 'mm',
                                                                'identicon',
                                                                'monsterid',
                                                                'wavatar']:
                return accounts_settings.ACCOUNTS_GRAVATAR_DEFAULT
            else: return None

    def get_full_name_or_username(self):
        """
        Returns the full name of the user, or if none is supplied will return
        the username.

        Also looks at ``ACCOUNTS_WITHOUT_USERNAMES`` settings to define if it
        should return the username or email address when the full name is not
        supplied.

        :return:
            ``String`` containing the full name of the user. If no name is
            supplied it will return the username or email address depending on
            the ``ACCOUNTS_WITHOUT_USERNAMES`` setting.

        """
        user = self.user
        if user.first_name or user.last_name:
            # We will return this as translated string. Maybe there are some
            # countries that first display the last name.
            name = _("%(first_name)s %(last_name)s") % \
                {'first_name': user.first_name,
                 'last_name': user.last_name}
        else:
            # Fallback to the username if usernames are used
            if not accounts_settings.ACCOUNTS_WITHOUT_USERNAMES:
                name = "%(username)s" % {'username': user.username}
            else:
                name = "%(email)s" % {'email': user.email}
        return name.strip()
