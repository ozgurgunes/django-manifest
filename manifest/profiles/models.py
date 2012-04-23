# -*- coding: utf8 -*-
import re
import datetime
from dateutil import relativedelta
from django.conf import settings
from django.db import models, transaction
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.localflavor.us.models import PhoneNumberField
from django_countries import CountryField

from manifest.accounts.models import ProfileBase
from manifest.accounts.utils import get_profile_model
from manifest.facebook.models import ProfileBase as FacebookProfileBase

class Profile(ProfileBase, FacebookProfileBase):
    """
    Profile model
    
    """
        
    about               = models.TextField(_('about'), blank=True, null=True)
    education           = models.CharField(_('education'), max_length=128, blank=True, null=True)
    occupation          = models.CharField(_('occupation'), max_length=64, blank=True, null=True)
    location            = models.CharField(_('location'), blank=True, null=True, max_length=64)
    website             = models.URLField(_('website'), blank=True, null=True)
    mobile              = PhoneNumberField(_('mobile'), blank=True, null=True)
    country             = CountryField(_('country'), blank=True, null=True)
        
    class Meta:
        verbose_name = _('profile')
        verbose_name_plural = _('profiles')
    
    def __unicode__(self):
        return u"Profile of %s" % self.user
  
    def copy_facebook(self, response):
        """
        Updates profile 

        If no ``picture_type`` has been set, returns normal as default.

        :return:
            Updated profile

        """        
        self.birth_date = response.get('birthday')
        self.gender = response.get('gender').upper()[0]
        self.education = response.get('education')
        self.occupation = response.get('occupation')
        self.location = response.get('location')
        
        return super(Profile, self).copy_facebook(response)

    # def save(self, force_insert=False, force_update=False, *args, **kwargs):
    #     try:
    #         old_obj = Profile.objects.get(pk=self.pk)
    #         if old_obj.picture.path != self.picture.path:
    #             path = old_obj.picture.path
    #             default_storage.delete(path)
    #     except:
    #         pass
    #     super(Profile, self).save(force_insert, force_update, *args, **kwargs)

