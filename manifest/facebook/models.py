# -*- coding: utf-8 -*-
import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from social_auth.backends.facebook import FacebookBackend
from social_auth.signals import pre_update, socialauth_registered
from manifest.facebook.api import Graph
from manifest.accounts.utils import get_profile_model
from manifest.accounts.models import create_user_account
from manifest.facebook.utils import iso_time

class ProfileBase(models.Model):
    """Abstract base class for Facebook user profile"""

    facebook_id         = models.BigIntegerField(_(u'Facebook id'), unique=True, blank=True, null=True)
    facebook_token      = models.TextField(_(u'Facebook token'), blank=True, null=True)
    facebook_expires    = models.IntegerField(_(u'Facebook expires'), blank=True, null=True)
    facebook_username   = models.CharField(_(u'Facebook username'), max_length=255, blank=True)
    facebook_verified   = models.BooleanField(_(u'Facebook verified'), default=False, blank=True)
    facebook_link       = models.URLField(_(u'Facebook link'), blank=True, null=True)

    class Meta:
        abstract        = True

    @property
    def facebook_avatar(self, picture_type='normal'):
        """
        Returns Facebook profile picture

        If no ``picture_type`` has been set, returns normal as default.

        :return:
            Url of profile picture

        """
        return 'https://graph.facebook.com/%s/picture?type=%s' % (self.facebook_id, picture_type)

    def copy_facebook(self, response):
        """
        Updates profile 

        If no ``picture_type`` has been set, returns normal as default.

        :return:
            Updated profile

        """
        self.facebook_id        = response.get('id')
        self.facebook_token     = response.get('access_token')
        self.facebook_expires   = response.get('expires')
        self.facebook_username  = response.get('username')
        self.facebook_verified  = response.get('verified')        
        self.facebook_link      = response.get('link')        
        
        # self.birth_date = response.get('birthday')
        # self.gender = response.get('gender').upper()[0]
        # self.education = response.get('education')
        # self.occupation = response.get('occupation')
        # self.location = response.get('location')
        # 
        return self.save()

    def copy_friends(self, friends):
        """
        Copies Facebook friends

        """
        old_friends = FacebookFriend.objects.filter(user=self.user).delete()
        return FacebookFriend.objects.bulk_create(
                        [FacebookFriend(user=self.user, 
                            facebook_id=friend['id'], name=friend['name']) for friend in friends]
                        )

    def copy_likes(self, likes):
        """
        Copies Facebook likes

        """
        old_likes = FacebookLike.objects.filter(user=self.user).delete()
        return FacebookLike.objects.bulk_create(
                        [FacebookLike(user=self.user, 
                            facebook_id=like['id'], name=like['name'], category=like['category'], 
                            created_time=iso_time(like['created_time'])) for like in likes]
                        )
        
class FacebookLike(models.Model):
    """Abstract base class for Facebook user profile"""

    user = models.ForeignKey(User, verbose_name=_(u'User'))

    facebook_id = models.BigIntegerField(_(u'Facebook id'))    
    name = models.CharField(_(u'Name'), max_length=128, blank=True, null=True)
    category = models.CharField(_(u'Category'), max_length=128, blank=True, null=True)
    created_time =  models.DateTimeField(_(u'Created time'), blank=True, null=True)
    
    class Meta:
        db_table = 'facebook_likes'
        abstract        = False if settings.MANIFEST_FACEBOOK_LIKES else True

    def __unicode__(self):
        return 'likes of %s' % self.user.username

class FacebookFriend(models.Model):
    """Abstract base class for Facebook user profile"""

    user = models.ForeignKey(User, verbose_name=_(u'User'))

    facebook_id = models.BigIntegerField(_(u'Facebook id'))    
    name = models.CharField(_(u'Name'), max_length=128, blank=True, null=True)
    
    class Meta:
        db_table = 'facebook_friends'
        abstract        = False if settings.MANIFEST_FACEBOOK_FRIENDS else True
        
    def __unicode__(self):
        return 'friends of %s' % self.user.username


def update_profile(sender, user, response, *args, **kwargs):
    try:
        profile = user.get_profile()
        profile.copy_facebook(response)
        facebook = Graph(user)    
        if 'friends' in settings.MANIFEST_FACEBOOK_SYNC:
            friends = profile.copy_friends(facebook.get('friends'))
        if 'likes' in settings.MANIFEST_FACEBOOK_SYNC:
            likes = profile.copy_likes(facebook.get('likes'))
    except:
        pass
    
def register_profile(sender, user, response, *args, **kwargs):
    try:
        try:
            profile = user.get_profile()
        except:
            create_user_account(user)
            profile = user.get_profile()
        profile.copy_facebook(response)    
        facebook = Graph(user)    
        if settings.MANIFEST_FACEBOOK_FRIENDS:
            friends = profile.copy_friends(facebook.get('friends'))
        if settings.MANIFEST_FACEBOOK_LIKES:
            likes = profile.copy_likes(facebook.get('likes'))
    except:
        pass
    
pre_update.connect(update_profile, sender=FacebookBackend)
socialauth_registered.connect(register_profile, sender=FacebookBackend)
