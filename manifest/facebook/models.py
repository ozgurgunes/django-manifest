# -*- coding: utf-8 -*-
import settings
from django.conf import settings as django_settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from manifest.facebook.api import Graph
from manifest.facebook.utils import iso_time

class ProfileBase(models.Model):
    """
    Abstract base class for Facebook user profile
    
    """

    facebook_id         = models.BigIntegerField(_(u'Facebook id'), 
                                unique=True, blank=True, null=True)
    facebook_token      = models.TextField(_(u'Facebook token'), 
                                blank=True, null=True)
    facebook_expires    = models.IntegerField(_(u'Facebook expires'), 
                                blank=True, null=True)
    facebook_username   = models.CharField(_(u'Facebook username'), 
                                max_length=255, blank=True)
    facebook_verified   = models.BooleanField(_(u'Facebook verified'), 
                                default=False, blank=True)
    facebook_link       = models.URLField(_(u'Facebook link'), 
                                blank=True, null=True)

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
        return 'https://graph.facebook.com/%s/picture?type=%s' % (
                    self.facebook_id, picture_type)

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
        
        return self.save()

    def copy_friends(self, friends):
        """
        Copies Facebook friends

        """
        old_friends = FacebookFriend.objects.filter(user=self.user).delete()
        return FacebookFriend.objects.bulk_create([
                        FacebookFriend(user=self.user, 
                            facebook_id=friend['id'], 
                            name=friend['name']) for friend in friends])

    def copy_likes(self, likes):
        """
        Copies Facebook likes

        """
        old_likes = FacebookLike.objects.filter(user=self.user).delete()
        return FacebookLike.objects.bulk_create([
                        FacebookLike(user=self.user, 
                            facebook_id=like['id'], 
                            name=like['name'], 
                            category=like['category'], 
                            created_time=iso_time(
                                like['created_time'])) for like in likes])
        
class FacebookLike(models.Model):
    """
    Abstract base class for Facebook user profile
    
    """

    user = models.ForeignKey(django_settings.AUTH_USER_MODEL, verbose_name=_(u'User'))

    facebook_id     = models.BigIntegerField(_(u'Facebook id'))    
    name            = models.CharField(_(u'Name'), max_length=128, 
                            blank=True, null=True)
    category        = models.CharField(_(u'Category'), max_length=128, 
                            blank=True, null=True)
    created_time    =  models.DateTimeField(_(u'Created time'), 
                            blank=True, null=True)
    
    class Meta:
        db_table = 'facebook_likes'
        abstract = False if settings.MANIFEST_FACEBOOK_LIKES else True

    def __unicode__(self):
        return 'likes of %s' % self.user.username

class FacebookFriend(models.Model):
    """
    Abstract base class for Facebook user profile
    
    """

    user = models.ForeignKey(django_settings.AUTH_USER_MODEL, verbose_name=_(u'User'))

    facebook_id = models.BigIntegerField(_(u'Facebook id'))    
    name = models.CharField(_(u'Name'), max_length=128, blank=True, null=True)
    
    class Meta:
        db_table = 'facebook_friends'
        abstract = False if settings.MANIFEST_FACEBOOK_FRIENDS else True
        
    def __unicode__(self):
        return 'friends of %s' % self.user.username


def update_profile(sender, user, response, *args, **kwargs):
    try:
        user.copy_facebook(response)
        facebook = Graph(user)    
        if 'friends' in settings.MANIFEST_FACEBOOK_SYNC:
            friends = user.copy_friends(facebook.get('friends'))
        if 'likes' in settings.MANIFEST_FACEBOOK_SYNC:
            likes = user.copy_likes(facebook.get('likes'))
    except:
        pass
    
def register_profile(sender, user, response, *args, **kwargs):
    try:
        user.copy_facebook(response)    
        facebook = Graph(user)    
        if settings.MANIFEST_FACEBOOK_FRIENDS:
            friends = user.copy_friends(facebook.get('friends'))
        if settings.MANIFEST_FACEBOOK_LIKES:
            likes = user.copy_likes(facebook.get('likes'))
    except:
        pass
    
