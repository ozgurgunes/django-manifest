from django.forms.extras.widgets import SelectDateWidget
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from manifest.profiles.models import Profile
from django.forms.models import inlineformset_factory
from manifest.profiles.models import *
import unicodedata
from datetime import datetime
from django import forms
from django_countries import countries

class ProfileForm(forms.ModelForm):
    GENDER_CHOICES = (
        ('F', _('Female')),
        ('M', _('Male')),
    )
    about               = forms.CharField(widget=forms.Textarea(attrs={'class': 'textarea', 'rows': 5}), required=False)
    gender              = forms.ChoiceField(choices=GENDER_CHOICES, widget=forms.RadioSelect())
    birth_date          = forms.DateField(widget=SelectDateWidget(years=range(datetime.today().year-99, datetime.today().year-10)))
    occupation          = forms.CharField(max_length=24, required=False, widget=forms.TextInput(attrs={'class':'text'}))
    location            = forms.CharField(label=_('location'), required=False, max_length=64, widget=forms.TextInput(attrs={'class':'text'}))
    country             = forms.ChoiceField(choices=list([('','')] + list(countries.COUNTRIES_PLUS)))
    
    class Meta:
        model       = Profile
        fields     = ['gender', 'birth_date', 'occupation', 'about', 'location', 'country']

class MugshotForm(forms.ModelForm):
    gender              = forms.CharField(widget=forms.HiddenInput(), required=False)
    mugshot             = forms.ImageField(required=True)
    
    class Meta:
        model = Profile
        fields = ['mugshot', 'gender']

    def clean_mugshot(self):
        from StringIO import StringIO  
        from PIL import Image

        if self.cleaned_data.get('mugshot'):
            mugshot_data = self.cleaned_data['mugshot']
            if 'error' in mugshot_data:
                raise forms.ValidationError(_('Upload a valid image. The file you uploaded was either not an image or a corrupted image.'))
                
            content_type = mugshot_data.content_type
            if content_type:
                main, sub = content_type.split('/')
                if not (main == 'image' and sub in ['jpeg', 'gif', 'png']):
                    raise forms.ValidationError(_('JPEG, PNG, GIF only.'))
        
        if mugshot_data.size > 1024 * 1024:
            raise forms.ValidationError(_('Image size too big, max allowed size is 1MB'))
        """
        x, y = Image.open(mugshot_data.temporary_file_path()).size
        if y < 128 or x < 128:  
            raise forms.ValidationError(_('Upload a valid image. This one is too small in size.'))  
        """            
        return self.cleaned_data['mugshot']

class NameForm(forms.ModelForm):
    first_name          = forms.CharField(max_length=32, required=True, widget=forms.TextInput(attrs={'class':'text'}))
    last_name          = forms.CharField(max_length=32, required=True, widget=forms.TextInput(attrs={'class':'text'}))
    class Meta:
        model = User
        fields = ('first_name', 'last_name')
        
class EmailForm(forms.ModelForm):
    email = forms.EmailField(widget=forms.TextInput(attrs=dict({'class': 'text email'},
                                                               maxlength=75)), label=_(u'Email address'))
    class Meta:
        model       = User
        fields     = ['email']

    def clean_email(self):
        """
        Validate that the supplied email address is unique for the
        site.
        
        """
        if User.objects.filter(email__iexact=self.cleaned_data['email']).exclude(username=self.instance.username):
            raise forms.ValidationError(_(u'This email address is already in use. Please supply a different email address.'))
        return self.cleaned_data['email']

class NewPasswordForm(forms.Form):
    """
    A form that lets a user change set his/her password without
    entering the old password
    """
    new_password1 = forms.CharField(label=_("New password"), widget=forms.PasswordInput(attrs=dict({'class':'password text'})))
    new_password2 = forms.CharField(label=_("New password confirmation"), widget=forms.PasswordInput(attrs=dict({'class':'password text'})))

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(SetPasswordForm, self).__init__(*args, **kwargs)

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(_("The two password fields didn't match."))
        return password2

    def save(self, commit=True):
        self.user.set_password(self.cleaned_data['new_password1'])
        if commit:
            self.user.save()
        return self.user
                
class PasswordForm(NewPasswordForm):
    """
    A form that lets a user change his/her password by entering
    their old password.
    """
    old_password = forms.CharField(label=_("Old password"), widget=forms.PasswordInput(attrs=dict({'class':'password text'})))

    def clean_old_password(self):
        """
        Validates that the old_password field is correct.
        """
        old_password = self.cleaned_data["old_password"]
        if not self.user.check_password(old_password):
            raise forms.ValidationError(_("Your old password was entered incorrectly. Please enter it again."))
        return old_password
PasswordForm.base_fields.keyOrder = ['old_password', 'new_password1', 'new_password2']

class ServiceForm(forms.ModelForm):
    username            = forms.CharField(label=_('username'), required=False, max_length=32, widget=forms.TextInput(attrs={'class':'half text'}))
    class Meta:
        model       = Service

class LinkForm(forms.ModelForm):
    title           = forms.CharField(label=_('title'), required=False, max_length=100, widget=forms.TextInput(attrs={'class':'text'}))
    url             = forms.CharField(label=_('url'), required=False, widget=forms.TextInput(attrs={'class':'text'}))
    class Meta:
        model       = Link

ServiceFormSet  = inlineformset_factory(Profile, Service, form=ServiceForm)
LinkFormSet     = inlineformset_factory(Profile, Link, form=LinkForm)
