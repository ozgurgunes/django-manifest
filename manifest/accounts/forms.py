# -*- coding: utf-8 -*-
import random
import hashlib
from datetime import datetime
from StringIO import StringIO  
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.db.models import Q

from django.forms.extras.widgets import SelectDateWidget
from django.db.transaction import commit_on_success

from manifest.accounts import defaults

attrs_dict = {'class': 'required'}


class RegistrationForm(UserCreationForm):
    """
    Form for creating a new user account.

    Validates that the requested username and email is not already in use.
    Also requires the password to be entered twice.

    """
    username = forms.RegexField(label=_(u"Username"), 
                                regex=r'^\w+$', max_length=30,
                                widget=forms.TextInput(attrs=attrs_dict),                                
                                error_messages={'invalid': _(u'Username must '
                                    'contain only letters, numbers and underscores.')})

    email = forms.EmailField(label=_(u"Email address"), 
                                widget=forms.TextInput(
                                    attrs=dict(attrs_dict, maxlength=75)))

    password1 = forms.CharField(label=_("Password"), 
                                    widget=forms.PasswordInput(
                                        attrs=attrs_dict))
    password2 = forms.CharField(label=_("Password confirmation"), 
                                    widget=forms.PasswordInput(
                                        attrs=attrs_dict))
            
    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'password1', 'password2']

    def clean_username(self):
        """
        Validate that the username is unique and not listed 
        in ``defaults.ACCOUNTS_FORBIDDEN_USERNAMES`` list.
        
        """
        try: 
            user = get_user_model().objects.get(username=self.cleaned_data["username"])
        except get_user_model().DoesNotExist: 
            pass
        else: 
            raise forms.ValidationError(
                            self.error_messages['duplicate_username'])

        if self.cleaned_data['username'].lower() \
            in defaults.ACCOUNTS_FORBIDDEN_USERNAMES:
            raise forms.ValidationError(_(u'This username is not allowed.'))
        return self.cleaned_data['username']

    def clean_email(self):
        """ 
        Validate that the email address is unique. 
        
        """
        if get_user_model().objects.filter(
            Q(email__iexact=self.cleaned_data['email']) |
            Q(email_unconfirmed__iexact=self.cleaned_data['email'])):
            raise forms.ValidationError(_(u'This email address is already '
                        'in use. Please supply a different email.'))
        return self.cleaned_data['email']

    def save(self):
        """ 
        Creates a new user and account. Returns the newly created user. 
        
        """
        username, email, password = (self.cleaned_data['username'],
                                     self.cleaned_data['email'],
                                     self.cleaned_data['password1'])

        user = get_user_model().objects.create_user(username, email, password,
                        not defaults.ACCOUNTS_ACTIVATION_REQUIRED, 
                            defaults.ACCOUNTS_ACTIVATION_REQUIRED)
        return user

class RegistrationFormOnlyEmail(RegistrationForm):
    """
    Form for creating a new user account but not needing a username.

    This form is an adaptation of :class:`RegistrationForm`. It's used 
    when ``ACCOUNTS_WITHOUT_USERNAME`` setting is set to ``True``. 
    And thus the user is not asked to supply an username, but one is 
    generated for them. The user can than keep sign in by using their email.

    """
    def __init__(self, *args, **kwargs):
        super(RegistrationFormOnlyEmail, self).__init__(*args, **kwargs)
        del self.fields['username']

    def save(self):
        """ 
        Generate a random username before falling back to parent 
        register form. 
        
        """
        while True:
            username = hashlib.sha1(str(random.random())).hexdigest()[:5]
            try:
                get_user_model().objects.get(username__iexact=username)
            except get_user_model().DoesNotExist: break

        self.cleaned_data['username'] = username
        return super(RegistrationFormOnlyEmail, self).save()

class RegistrationFormToS(RegistrationForm):
    """ 
    Add a Terms of Service button to the ``RegistrationForm``. 
    
    """
    tos = forms.BooleanField(widget=forms.CheckboxInput(attrs=attrs_dict),
                             label=_(u'I have read and agree to the '
                                'Terms of Service.'),
                             error_messages={'required': _(u'You must '
                                'agree to the terms to register.')})

def identification_field_factory(label, error_required):
    """
    A simple identification field factory which enable you to set the label.

    :param label:
        String containing the label for this field.

    :param error_required:
        String containing the error message if the field is left empty.

    """
    return forms.CharField(label=_(u"%(label)s") % {'label': label},
                           widget=forms.TextInput(attrs=attrs_dict),
                           max_length=75,
                           error_messages={'required': _(u"%(error)s") % 
                                            {'error': error_required}})

class AuthenticationForm(forms.Form):
    """
    A custom form where the identification can be a email address or username.

    """
    identification = identification_field_factory(_(u"Email"),
                                                  _(u"Either supply us with "
                                                    "your email or username."))
    password = forms.CharField(label=_(u"Password"),
                               widget=forms.PasswordInput(
                                    attrs=attrs_dict, render_value=False))
    remember_me = forms.BooleanField(widget=forms.CheckboxInput(),
                                     required=False,
                                     label=_(u'Remember me for %(days)s') % 
                        {'days': _(defaults.ACCOUNTS_REMEMBER_ME_DAYS[0])})

    def __init__(self, *args, **kwargs):
        """ 
        A custom init because we need to change the label if no 
        usernames is used 
        
        """
        self.user_cache = None
        super(AuthenticationForm, self).__init__(*args, **kwargs)
        if defaults.ACCOUNTS_WITHOUT_USERNAMES:
            self.fields['identification'] = identification_field_factory(
                                                _(u"Email address"),
                                                _(u"Please supply your "
                                                    "email address."))

    def clean(self):
        """
        Checks for the identification and password.

        If the combination can't be found will raise an invalid sign in error.

        """
        identification = self.cleaned_data.get('identification')
        password = self.cleaned_data.get('password')

        if identification and password:
            self.user_cache = authenticate(identification=identification, 
                                password=password)
            if self.user_cache is None:
                raise forms.ValidationError(_(u"Please enter a correct "
                        "username or email address and password. "
                        "Note that both fields are case-sensitive."))
        return self.cleaned_data
    
    def get_user(self):
        return self.user_cache

class EmailForm(forms.Form):
    email = forms.EmailField(label=_(u"New email"), required=True,
                                widget=forms.TextInput(
                                    attrs=dict(attrs_dict, maxlength=75)))

    def __init__(self, user, *args, **kwargs):
        """
        The current ``user`` is needed for initialisation of this form so
        that we can check if the email address is still free and not always
        returning ``True`` for this query because it's the users own email
        address.

        """
        super(EmailForm, self).__init__(*args, **kwargs)
        if not isinstance(user, get_user_model()):
            raise TypeError, "user must be an instance of User"
        else: self.user = user

    def clean_email(self):
        """ 
        Validate that the email is not already registered with another user.
        
        """
        if self.cleaned_data['email'].lower() == self.user.email:
            raise forms.ValidationError(_(u"You're already known under "
                                                "this email address."))
        if get_user_model().objects.filter(
                email__iexact=self.cleaned_data['email']).exclude(
                    email__iexact=self.user.email):
            raise forms.ValidationError(_(u'This email address is already '
                        'in use. Please supply a different email address.'))
        return self.cleaned_data['email']

    def save(self):
        """
        Save method calls :func:`user.change_email()` method which sends out 
        an email with an verification key to verify and with it enable this 
        new email address.

        """
        return self.user.change_email(self.cleaned_data['email'])

class NameForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=False, 
                        widget=forms.TextInput(attrs={'class':'text'}))
    last_name = forms.CharField(max_length=30, required=False, 
                        widget=forms.TextInput(attrs={'class':'text'}))
    class Meta:
        model = get_user_model()
        fields = ('first_name', 'last_name')

class ProfileForm(forms.ModelForm):
    """ Base form used for fields that are always required """

    GENDER_CHOICES = (
        ('F', _(u'Female')),
        ('M', _(u'Male')),
    )

    first_name = forms.CharField(label=_(u'First name'),
                                 max_length=30,
                                 required=False)
    last_name = forms.CharField(label=_(u'Last name'),
                                max_length=30,
                                required=False)

    gender = forms.ChoiceField(required=False, choices=GENDER_CHOICES, 
                    widget=forms.RadioSelect())
    birth_date = forms.DateField(required=False, 
                    widget=SelectDateWidget(
                        years=range(datetime.today().year-99, 
                                    datetime.today().year-10)))

    class Meta:
        model = get_user_model()
        exclude = ['user']

    def clean_picture(self):
        """
        Validates format and file size of uploaded profile picture.
        
        """
        if self.cleaned_data.get('picture'):
            picture_data = self.cleaned_data['picture']
            if 'error' in picture_data:
                raise forms.ValidationError(_(u'Upload a valid image. '
                            'The file you uploaded was either not an image '
                            'or a corrupted image.'))
                
            content_type = picture_data.content_type
            if content_type:
                main, sub = content_type.split('/')
                if not (main == 'image' 
                            and sub in defaults.ACCOUNTS_PICTURE_FORMATS):
                    raise forms.ValidationError(_(u'%s only.' % 
                                    defaults.ACCOUNTS_PICTURE_FORMATS))
        
            if picture_data.size > int(defaults.ACCOUNTS_PICTURE_MAX_FILE):
                raise forms.ValidationError(_(u'Image size is too big.'))
            return self.cleaned_data['picture']

