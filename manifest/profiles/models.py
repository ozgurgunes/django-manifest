import re
import datetime
from dateutil import relativedelta
from django.db import models, transaction
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.localflavor.us.models import PhoneNumberField
from django.core.files.storage import default_storage
from django_countries import CountryField

from manifest.accounts.models import ProfileBase

def get_upload_to(instance, filename):
    return '%s/%s/%s' % (str(instance._meta.app_label), str(instance._meta.module_name), re.sub('[^\.0-9a-zA-Z()_-]', '_', filename))
    
class Profile(ProfileBase):
    """
    Profile model
    
    """
    
    GENDER_CHOICES = (
        ('F', _('Female')),
        ('M', _('Male')),
    )

    user                = models.OneToOneField(User, unique=True, verbose_name=_('user'), related_name='profile')
    
    # mugshot             = models.ImageField(_('mugshot'), upload_to=get_upload_to, blank=True)
    status              = models.CharField(_('status'), max_length=196, blank=True, null=True)
    about               = models.TextField(_('about'), blank=True, null=True)
    birth_date          = models.DateField(_('birth date'), blank=True, null=True)
    gender              = models.CharField(_('gender'), choices=GENDER_CHOICES, max_length=1, blank=True, null=True)
    occupation          = models.CharField(_('occupation'), max_length=32, blank=True, null=True)
    mobile              = PhoneNumberField(_('mobile'), blank=True, null=True)
    location            = models.CharField(_('location'), blank=True, null=True, max_length=64)
    country             = CountryField(_('country'), blank=True, null=True)
        
    class Meta:
        verbose_name = _('profile')
        verbose_name_plural = _('profiles')
    
    def __unicode__(self):
        return u"Profile of %s" % self.user
  
    @models.permalink
    def get_absolute_url(self):
        return ('profiles_profile_detail', None, { 'username': self.user.username })


    @property
    def age(self):
        TODAY = datetime.date.today()
        if self.birth_date:
            return u"%s" % relativedelta.relativedelta(TODAY, self.birth_date).years
        else:
            return None

    @property
    def avatar(self):
        if not self.mugshot:
            self.mugshot = u'profiles/profile/_default.png'
        return self.mugshot

    @property
    def sms_address(self):
        if (self.mobile and self.mobile_provider):
            return u"%s@%s" % (re.sub('-', '', self.mobile), self.mobile_provider.domain)

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        try:
            old_obj = Profile.objects.get(pk=self.pk)
            if old_obj.mugshot.path != self.mugshot.path:
                path = old_obj.mugshot.path
                default_storage.delete(path)
        except:
            pass
        super(Profile, self).save(force_insert, force_update, *args, **kwargs)

# @transaction.commit_on_success()
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         Profile.objects.get_or_create(user=instance)
# 
# models.signals.post_save.connect(create_user_profile, sender=User)

class MobileProvider(models.Model):
    """ MobileProvider model """
    title             = models.CharField(_('title'), max_length=25)
    domain            = models.CharField(_('domain'), max_length=50, unique=True)

    class Meta:
        verbose_name = _('mobile provider')
        verbose_name_plural = _('mobile providers')
        db_table = 'profiles_mobile_providers'

    def __unicode__(self):
        return u"%s" % self.title


class ServiceType(models.Model):
    """ Service type model """
    title           = models.CharField(_('title'), blank=True, max_length=100)
    url             = models.URLField(_('url'), blank=True, help_text='URL with a single \'{user}\' placeholder to turn a username into a service URL.', verify_exists=False)

    class Meta:
        verbose_name = _('service type')
        verbose_name_plural = _('service types')
        db_table = 'profiles_service_type'

    def __unicode__(self):
        return u"%s" % self.title


class Service(models.Model):
    """ Service model """
    service         = models.ForeignKey(ServiceType)
    profile         = models.ForeignKey(Profile)
    username        = models.CharField(_('Name or ID'), max_length=32, help_text="Username or id to be inserted into the service url.")
    created         = models.DateTimeField(auto_now_add=True)
    modified        = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('service')
        verbose_name_plural = _('services')
    
    def __unicode__(self):
        return u"%s" % self.username
    
    @property
    def service_url(self):
        return re.sub('{user}', self.username, self.service.url)
    
    @property
    def title(self):
        return u"%s" % self.service.title


class Link(models.Model):
    """ Service type model """
    profile         = models.ForeignKey(Profile)
    title           = models.CharField(_('title'), max_length=100)
    url             = models.URLField(_('url'), verify_exists=True)

    class Meta:
        verbose_name = _('link')
        verbose_name_plural = _('links')

    def __unicode__(self):
        return u"%s" % self.title