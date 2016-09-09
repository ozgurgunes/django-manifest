# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.contrib.auth import (authenticate, login as auth_login, logout, 
                                    get_user_model, REDIRECT_FIELD_NAME)
from django.contrib.auth.forms import PasswordChangeForm
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.http import Http404
from django.views.generic import (View, ListView, DetailView, FormView, 
                                    CreateView, UpdateView, TemplateView)

from manifest.accounts.forms import (RegistrationForm, 
                                        RegistrationFormOnlyEmail, 
                                        AuthenticationForm,
                                        EmailForm, ProfileForm)
from manifest.accounts.decorators import secure_required
from manifest.accounts.utils import login_redirect
from manifest.accounts import signals as accounts_signals
from manifest.accounts import defaults



class ExtraContextMixin(View):
    """
    A mixin that passes ``extra_context`` dictionary as template context.
    
    """
    
    extra_context = {}

    def get_context_data(self, **kwargs):
        context = super(ExtraContextMixin, self).get_context_data(**kwargs)
        context.update(self.extra_context)
        return context
    
    
class SecureRequiredMixin(View):
    """
    A mixin that switches URL from http to https if ``ACCOUNTS_USE_HTTPS`` 
    setting is ``True``.
    """
    
    @method_decorator(secure_required)
    def dispatch(self, request, *args, **kwargs):
        return super(SecureRequiredMixin, self).dispatch(request, 
                                                    *args, **kwargs)


class LoginRequiredMixin(View):
    """
    A mixin that redirects user to login form if not authenticated yet.
    
    """
    
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(request, 
                                                    *args, **kwargs)


class Register(CreateView, ExtraContextMixin, SecureRequiredMixin):
    """
    Register user with a username, email and password. 
    
    Users receives an email with an activation link to activate their 
    account if ``ACCOUNTS_ACTIVATION_REQUIRED`` setting is ``True``. 
    
    Redirects to ``success_url`` if it is given, else redirects to 
    ``accounts_register_complete`` view.
    
    """
    
    model = get_user_model()
    template_name = 'accounts/register.html'
    success_message = _(u'You have been registered.')
    
    def get_form_class(self):
        if self.form_class: return self.form_class
        elif defaults.ACCOUNTS_WITHOUT_USERNAMES:
            return RegistrationFormOnlyEmail
        else: return RegistrationForm
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated(): 
            return redirect(reverse('accounts_settings'))
        return super(Register, self).dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        user = form.save()
        accounts_signals.registration_complete.send(sender=None, 
            user=user, request=self.request)
        if defaults.ACCOUNTS_USE_MESSAGES:
            messages.success(self.request, self.success_message, 
                fail_silently=True)
        if self.success_url: return redirect(self.success_url)
        else: return redirect(reverse('accounts_register_complete', 
                                kwargs={'username': user.username}))

class Login(FormView, ExtraContextMixin, SecureRequiredMixin):
    """
    Authenticate user by email or username with password. 
    
    When the identification is correct and the user ``is_active`` 
    user will be redirected to ``success_url`` if it is defined. 
    
    If ``success_url`` is not defined, the ``login_redirect`` function  
    will be called with the arguments ``REDIRECT_FIELD_NAME`` and an 
    instance of the ``User`` whois is trying the login. The returned 
    value of the function will be the URL that will be redirected to.

    Users can also select to be remembered for ``ACCOUNTS_REMEMBER_DAYS``.
    
    """
    
    form_class = AuthenticationForm
    template_name = 'accounts/login.html'
    success_message = _(u'You have been logged in.')
    
    def form_valid(self, form):
        user = form.get_user()
        if user.is_active:
            auth_login(self.request, user)
            if form.cleaned_data['remember_me']:
                self.request.session.set_expiry(
                    defaults.ACCOUNTS_REMEMBER_ME_DAYS[1] * 86400)
            else: self.request.session.set_expiry(0)
            if defaults.ACCOUNTS_USE_MESSAGES:
                messages.success(self.request, self.success_message, 
                    fail_silently=True)
            if self.success_url: 
                return redirect(self.success_url)
            else: 
                url = login_redirect(
                        self.request.REQUEST.get(REDIRECT_FIELD_NAME), user)
                return redirect(url)
        else: 
            return redirect(reverse('accounts_disabled', 
                        kwargs={'username': user.username}))

class Activate(TemplateView, ExtraContextMixin):
    """
    Activate the user with the activation key.

    The key is a SHA1 string. When the SHA1 is found with username
    the ``User`` of that account will be activated.  
    
    After a successfull activation user will be redirected to
    ``accounts_profile_detail`` view if ``succes_url`` is not defined. 
    
    If the SHA1 is not found, the user will be shown the
    ``template_name`` template displaying a fail message.
        
    """
    
    template_name = 'accounts/activate_fail.html'
    success_message = _(u'Your account has been activated.')
    success_url = None

    def get_success_url(self, **kwargs):
        if self.success_url: return self.success_url % kwargs
        else: return reverse('accounts_profile_detail', 
                        kwargs={'username': self.kwargs['username']})
        
    def get(self, request, username, activation_key, *args, **kwargs):
        user = get_user_model().objects.activate_user(username, activation_key)
        if user:
            # Sign the user in.
            auth_login(request, authenticate(identification=user.email, 
                                                check_password=False))
            if defaults.ACCOUNTS_USE_MESSAGES:
                messages.success(self.request, self.success_message, 
                                    fail_silently=True)
            return redirect(self.get_success_url(**kwargs))
        return super(Activate, self).get(request, *args, **kwargs)            

class ProfileUpdate(UpdateView, SecureRequiredMixin, LoginRequiredMixin):
    """
    Update profile of current user
    
    Updates profile information for ``request.user``. User will be
    redirected to ``accounts_settings`` view in ``success_url`` is not
    defined.

    """
    
    model = get_user_model()
    profile_form = ProfileForm
    fields = ['first_name', 'last_name', 'gender', 'birth_date', 'picture', 
                    'timezone', 'locale']
    template_name = 'accounts/profile_form.html'
    success_message = _(u'Your profile has been updated.')
    
    def get_object(self):
        return self.request.user

    def get_initial(self):
        return {'first_name': self.request.user.first_name, 
                'last_name': self.request.user.last_name}

    def form_valid(self, form):
        profile = form.save()
        if defaults.ACCOUNTS_USE_MESSAGES:
            messages.success(self.request, self.success_message, 
                fail_silently=True)
        if self.success_url: return redirect(self.success_url)
        else: return redirect(reverse('accounts_settings'))


class PasswordChange(FormView, SecureRequiredMixin, LoginRequiredMixin):
    """
    Change password of current user
    
    Changes password for ``request.user``. User will be redirected to
    ``accounts_password_change_done`` view if ``success_url`` is not defined.

    """
    
    form_class = PasswordChangeForm
    template_name = 'accounts/password_change_form.html'
    
    def get_form_kwargs(self, **kwargs):
        kwargs = super(PasswordChange, self).get_form_kwargs(**kwargs)
        kwargs['user'] = self.request.user
        return kwargs
        
    def form_valid(self, form):
        user = form.save()
        accounts_signals.password_complete.send(sender=None, user=user)
        if self.success_url: return redirect(self.success_url)
        else: return redirect(reverse('accounts_password_change_done', 
                                kwargs={'username': user.username}))
                    

class EmailChange(PasswordChange):
    """
    Change email of current user
    
    Changes email for ``request.user``. Change will not be applied 
    until user confirm their new email.
    
    User will be redirected to ``accounts_email_change_done`` view 
    if ``success_url`` is not defined.
            
    """

    form_class = EmailForm
    template_name = 'accounts/email_change_form.html'
    
    def form_valid(self, form):
        user = form.save()
        if self.success_url: return redirect(self.success_url)
        else: 
            return redirect(reverse('accounts_email_change_done', 
                                kwargs={'username': user.username}))


class EmailConfirm(Activate, ExtraContextMixin):
    """
    Confirm the email address with username and confirmation key.

    Confirms the new email address by running 
    ``get_user_model().objects.confirm_email`` method.
    
    User will be redirected to ``accounts_email_change_complete`` view 
    if ``success_url`` is not defined. 
    
    If no ``User`` object returned the user will be shown the
    ``template_name`` template displaying a fail message.
    
    """
    
    template_name = 'accounts/email_change_fail.html'
    
    def get_success_url(self, **kwargs):
        if self.success_url: return self.success_url % kwargs
        else: return reverse('accounts_email_change_complete', 
                        kwargs={'username': self.kwargs['username']})

    def get(self, request, username, confirmation_key, *args, **kwargs):
        user = get_user_model().objects.confirm_email(username,
                                                         confirmation_key)
        if user:
            return redirect(self.get_success_url(**kwargs))
        return super(EmailConfirm, self).get(request, username, 
                                                        confirmation_key, 
                                                        *args, **kwargs)


class UserTemplateView(DetailView, LoginRequiredMixin, ExtraContextMixin):
    """
    Template view for current user
    
    Simple detail view gets ``request.user`` object.
    
    """
    
    template_name='accounts/settings.html'
    
    def get_object(self):
        return self.request.user


class UserView(DetailView, ExtraContextMixin):

    """
    Template view for current user account
    
    Simple detail view gets account by ``username`` as object.

    """

    queryset = get_user_model().objects.select_related().all()
    template_name = "accounts/settings.html"
    slug_field = 'username'
    slug_url_kwarg = 'username'


class ProfileList(ListView, ExtraContextMixin):
    """
    List active user profiles
    
    Lists active user profiles if ``ACCOUNTS_DISABLE_PROFILE_LIST``
    setting is True. Otherwise raises Http404.
    
    """

    queryset = get_user_model().objects.get_visible_profiles()
    template_name = "accounts/profile_list.html"
    
    def dispatch(self, request, *args, **kwargs):
        if defaults.ACCOUNTS_DISABLE_PROFILE_LIST \
           and not request.user.is_superuser:
            raise Http404
        return super(ProfileList, self).dispatch(request, *args, **kwargs)
        

class ProfileDetail(UserView, ExtraContextMixin):
    """
    Shows active user profile
    
    Simple detail view that displays an active user profile by username.
        
    """

    queryset = get_user_model().objects.get_visible_profiles()
    template_name = "accounts/profile_detail.html"
    slug_field = 'username'
    slug_url_kwarg = 'username'
    
