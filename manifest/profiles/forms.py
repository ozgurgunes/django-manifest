# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.forms.models import inlineformset_factory
from django_countries import countries
from manifest.accounts.forms import ProfileForm as BaseProfileForm
from manifest.accounts.utils import get_profile_model
from manifest.profiles.models import Profile
from manifest.facebook.forms import FacebookProfileForm

class ProfileForm(FacebookProfileForm):
    about               = forms.CharField(widget=forms.Textarea(attrs={'class': 'textarea', 'rows': 5}), required=False)
    occupation          = forms.CharField(max_length=24, required=False, widget=forms.TextInput(attrs={'class':'text'}))
    location            = forms.CharField(required=False, max_length=64, widget=forms.TextInput(attrs={'class':'text'}))
    country             = forms.ChoiceField(choices=list([('','')] + list(countries.COUNTRIES_PLUS)))
    
class ProfilePictureForm(FacebookProfileForm):
    user_id             = forms.CharField(widget=forms.HiddenInput(), required=False)
    picture             = forms.ImageField(required=True)
    
    class Meta:
        model = get_profile_model()
        exclude = ['first_name', 'last_name']
        fields = ['picture', 'user_id']

class NameForm(forms.ModelForm):
    first_name          = forms.CharField(max_length=32, required=True, widget=forms.TextInput(attrs={'class':'text'}))
    last_name          = forms.CharField(max_length=32, required=True, widget=forms.TextInput(attrs={'class':'text'}))
    class Meta:
        model = User
        fields = ('first_name', 'last_name')
        