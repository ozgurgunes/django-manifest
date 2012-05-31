# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib.auth import (authenticate, login as auth_login, logout, 
                                    REDIRECT_FIELD_NAME)
from django.contrib.auth.forms import PasswordChangeForm
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.http import HttpResponseForbidden, Http404
from django.db.transaction import commit_on_success
from django.views.generic import (View, ListView, DetailView, FormView, 
                                    CreateView, UpdateView, TemplateView)

from manifest.accounts.forms import (RegistrationForm, 
                                        RegistrationFormOnlyEmail, 
                                        AuthenticationForm,
                                        EmailForm, ProfileForm)
from manifest.accounts.models import Account
from manifest.accounts.decorators import secure_required
from manifest.accounts.utils import login_redirect, get_profile_model
from manifest.accounts import signals as accounts_signals
from manifest.accounts import settings as accounts_settings


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
    Registers user with a username, email and password. 
    
    Users receives an email with an activation link to activate their 
    account if ``ACCOUNTS_ACTIVATION_REQUIRED`` setting is ``True``. 
    
    Redirects to ``success_url`` if it is given, else redirects to 
    ``accounts_register_complete`` view.
    
    Extends:
        CreateView, ExtraContextMixin, SecureRequiredMixin

    """
    
    model = User
    template_name = 'accounts/register.html'
    success_message = _(u'You have been registered.')
    
    def get_form_class(self):
        if self.form_class: return self.form_class
        elif accounts_settings.ACCOUNTS_WITHOUT_USERNAMES:
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
        if accounts_settings.ACCOUNTS_USE_MESSAGES:
            messages.success(self.request, self.success_message, 
                fail_silently=True)
        if self.success_url: return redirect(self.success_url)
        else: return redirect(reverse('accounts_register_complete', 
                                kwargs={'username': user.username}))

class Login(FormView, ExtraContextMixin, SecureRequiredMixin):
    """
    Authenticates user by combining email/username with password. 
    
    When the combination is correct and the user :func:`is_active` 
    user will be redirected to ``success_url`` if it is given. 
    
    If no ``success_url`` is given the :func:`login_redirect` is called 
    with the arguments ``REDIRECT_FIELD_NAME``  and an instance of the 
    :class:`User` whois is trying the login. The returned value of the 
    function will be the URL that is redirected to.

    Users can also select to be remembered for ``ACCOUNTS_REMEMBER_DAYS``.
    
    """
    
    form_class = AuthenticationForm
    template_name = 'accounts/login.html'
    success_message = _(u'You have been logged in.')
    
    def form_valid(self, form):
        user = authenticate(
                    identification=form.cleaned_data['identification'], 
                    password=form.cleaned_data['password'])
        if user.is_active:
            auth_login(self.request, user)
            if form.cleaned_data['remember_me']:
                self.request.session.set_expiry(
                    accounts_settings.ACCOUNTS_REMEMBER_ME_DAYS[1] * 86400)
            else: self.request.session.set_expiry(0)
            if accounts_settings.ACCOUNTS_USE_MESSAGES:
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
    Activates the user with an activation key.

    The key is a SHA1 string. When the SHA1 is found with an
    :class:`Account`, the :class:`User` of that account will be
    activated.  
    
    After a successfull activation the view will redirect to
    ``succes_url`` if it is given, else redirect to 
    ``accounts_profile_detail`` view.
    
    If the SHA1 is not found, the user will be shown the
    ``template_name`` template displaying a fail message.
        
    """
    
    template_name = 'accounts/activate_fail.html'
    success_url = None

    def get_success_url(self, **kwargs):
        if self.success_url: return self.success_url % kwargs
        else: return reverse('accounts_profile_detail', 
                        kwargs={'username': self.kwargs['username']})
        
    def get(self, request, username, activation_key, *args, **kwargs):
        user = Account.objects.activate_user(username, activation_key)
        if user:
            # Sign the user in.
            auth_login(request, authenticate(identification=user.email, 
                                    check_password=False))
            return redirect(self.get_success_url(**kwargs))
        return super(Activate, self).get(request, *args, **kwargs)            

class ProfileUpdate(UpdateView, SecureRequiredMixin, LoginRequiredMixin):
    
    model = get_profile_model()
    profile_form = ProfileForm
    template_name = 'accounts/profile_form.html'
    success_message = _(u'Your profile has been updated.')
    
    def get_object(self):
        return self.request.user.get_profile()

    def get_initial(self):
        return {'first_name': self.request.user.first_name, 
                'last_name': self.request.user.last_name}

    def form_valid(self, form):
        profile = form.save()
        if accounts_settings.ACCOUNTS_USE_MESSAGES:
            messages.success(self.request, self.success_message, 
                fail_silently=True)
        if self.success_url: return redirect(self.success_url)
        else: return redirect(reverse('accounts_settings'))


class PasswordChange(FormView, SecureRequiredMixin, LoginRequiredMixin):
    
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

    form_class = EmailForm
    template_name = 'accounts/email_change_form.html'
    
    def form_valid(self, form):
        user = form.save()
        if self.success_url: return redirect(self.success_url)
        else: 
            return redirect(reverse('accounts_email_change_done', 
                                kwargs={'username': user.username}))


class EmailConfirm(Activate, ExtraContextMixin):
    
    template_name = 'accounts/email_change_fail.html'
    
    def get_success_url(self, **kwargs):
        if self.success_url: return self.success_url % kwargs
        else: return reverse('accounts_email_change_complete', 
                        kwargs={'username': self.kwargs['username']})

    def get(self, request, username, confirmation_key, *args, **kwargs):
        user = Account.objects.confirm_email(username, confirmation_key)
        if user:
            return redirect(self.get_success_url(**kwargs))
        return super(EmailConfirm, self).get(request, *args, **kwargs)            


class UserView(DetailView, ExtraContextMixin):
    
    template_name='accounts/settings.html'
    
    def get_object(self):
        return self.request.user


class AccountView(DetailView, ExtraContextMixin):

    queryset = Account.objects.select_related().all()
    template_name = "accounts/settings.html"
    slug_field = 'user__username'
    slug_url_kwarg = 'username'


class ProfileList(ListView, ExtraContextMixin):

    queryset = get_profile_model().objects.get_visible_profiles()
    template_name = "accounts/profile_list.html"
    
    def dispatch(self, request, *args, **kwargs):
        if accounts_settings.ACCOUNTS_DISABLE_PROFILE_LIST \
           and not request.user.is_superuser:
            raise Http404
        return super(ProfileList, self).dispatch(request, *args, **kwargs)
        

class ProfileDetail(AccountView, ExtraContextMixin):

    queryset = get_profile_model().objects.get_visible_profiles()
    template_name = "accounts/profile_detail.html"
    
