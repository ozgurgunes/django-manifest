from django.views.generic.simple import direct_to_template
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout, REDIRECT_FIELD_NAME
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.views.generic import list_detail
from django.http import HttpResponseForbidden, Http404

from guardian.decorators import permission_required_or_403

from manifest.accounts.forms import (RegistrationForm, RegistrationFormOnlyEmail, AuthenticationForm,
                           EmailForm, ProfileForm, AccountForm)
from manifest.accounts.models import Account
from manifest.accounts.decorators import secure_required
from manifest.accounts.utils import login_redirect, get_profile_model
from manifest.accounts import signals as accounts_signals
from manifest.accounts import settings as accounts_settings

@secure_required
def login(request, auth_form=AuthenticationForm,
           template_name='accounts/login.html',
           redirect_field_name=REDIRECT_FIELD_NAME,
           redirect_login_function=login_redirect, extra_context=None):
    """
    Sign in using email or username with password.

    Signs a user in by combining email/username with password. If the
    combination is correct and the user :func:`is_active` the
    :func:`redirect_login_function` is called with the arguments
    ``REDIRECT_FIELD_NAME`` and an instance of the :class:`User` whois is
    trying the login. The returned value of the function will be the URL that
    is redirected to.

    A user can also select to be remembered for ``ACCOUNTS_REMEMBER_DAYS``.

    :param auth_form:
        Form to use for loging the user in. Defaults to the
        :class:`AuthenticationForm` supplied by accounts.

    :param template_name:
        String defining the name of the template to use. Defaults to
        ``accounts/login.html``.

    :param redirect_field_name:
        Form field name which contains the value for a redirect to the
        successing page. Defaults to ``next`` and is set in
        ``REDIRECT_FIELD_NAME`` setting.

    :param redirect_login_function:
        Function which handles the redirect. This functions gets the value of
        ``REDIRECT_FIELD_NAME`` and the :class:`User` who has logged in. It
        must return a string which specifies the URI to redirect to.

    :param extra_context:
        A dictionary containing extra variables that should be passed to the
        rendered template. The ``form`` key is always the ``auth_form``.

    **Context**

    ``form``
        Form used for authentication supplied by ``auth_form``.

    """
    form = auth_form

    if request.method == 'POST':
        form = auth_form(request.POST, request.FILES)
        if form.is_valid():
            identification, password, remember_me = (form.cleaned_data['identification'],
                                                     form.cleaned_data['password'],
                                                     form.cleaned_data['remember_me'])
            user = authenticate(identification=identification,
                                password=password)
            if user.is_active:
                auth_login(request, user)
                if remember_me:
                    request.session.set_expiry(accounts_settings.ACCOUNTS_REMEMBER_ME_DAYS[1] * 86400)
                else: request.session.set_expiry(0)

                if accounts_settings.ACCOUNTS_USE_MESSAGES:
                    messages.success(request, _('You have been logged in.'),
                                     fail_silently=True)

                # Whereto now?
                redirect_to = redirect_login_function(
                    request.REQUEST.get(redirect_field_name), user)
                return redirect(redirect_to)
            else:
                return redirect(reverse('accounts_disabled',
                                        kwargs={'username': user.username}))

    if not extra_context: extra_context = dict()
    extra_context.update({
        'form': form,
        'next': request.REQUEST.get(redirect_field_name),
    })
    return direct_to_template(request,
                              template_name,
                              extra_context=extra_context)

@secure_required
def register(request, registration_form=RegistrationForm,
           template_name='accounts/register.html', success_url=None,
           extra_context=None):
    """
    Signup of an account.

    Signup requiring a username, email and password. After register a user gets
    an email with an activation link used to activate their account. After
    successful register redirects to ``success_url``.

    :param registration_form:
        Form that will be used to sign a user. Defaults to accounts's
        :class:`RegistrationForm`.

    :param template_name:
        String containing the template name that will be used to display the
        register form. Defaults to ``accounts/registration_form.html``.

    :param success_url:
        String containing the URI which should be redirected to after a
        successfull register. If not supplied will redirect to
        ``accounts_register_complete`` view.

    :param extra_context:
        Dictionary containing variables which are added to the template
        context. Defaults to a dictionary with a ``form`` key containing the
        ``registration_form``.

    **Context**

    ``form``
        Form supplied by ``registration_form``.

    """
    # If no usernames are wanted and the default form is used, fallback to the
    # default form that doesn't display to enter the username.
    if accounts_settings.ACCOUNTS_WITHOUT_USERNAMES and (registration_form == RegistrationForm):
        registration_form = RegistrationFormOnlyEmail

    form = registration_form()

    if request.method == 'POST':
        form = registration_form(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()

            # Send the registration complete signal
            accounts_signals.registration_complete.send(sender=None, user=user, request=request)

            if success_url: 
                redirect_to = success_url
            else: 
                redirect_to = reverse('accounts_register_complete', kwargs={'username': user.username})

            # A new logged user should logout the old one.
            if request.user.is_authenticated():
                logout(request)
            return redirect(redirect_to)

    if not extra_context: extra_context = dict()
    extra_context['form'] = form
    return direct_to_template(request, template_name, extra_context=extra_context)

@secure_required
def activate(request, username, activation_key,
             template_name='accounts/activate_fail.html',
             success_url=None, extra_context=None):
    """
    Activate a user with an activation key.

    The key is a SHA1 string. When the SHA1 is found with an
    :class:`Account`, the :class:`User` of that account will be
    activated.  After a successfull activation the view will redirect to
    ``succes_url``.  If the SHA1 is not found, the user will be shown the
    ``template_name`` template displaying a fail message.

    :param username:
        String of the username that wants to be activated.

    :param activation_key:
        String of a SHA1 string of 40 characters long. A SHA1 is always 160bit
        long, with 4 bits per character this makes it --160/4-- 40 characters
        long.

    :param template_name:
        String containing the template name that is used when the
        ``activation_key`` is invalid and the activation failes. Defaults to
        ``accounts/activation_fail.html``.

    :param success_url:
        String containing the URL where the user should be redirected to after
        a succesfull activation. Will replace ``%(username)s`` with string
        formatting if supplied. If ``success_url`` is left empty, will direct
        to ``accounts_profile_detail`` view.

    :param extra_context:
        Dictionary containing variables which could be added to the template
        context. Default to an empty dictionary.

    """
    user = Account.objects.activate_user(username, activation_key)
    if user:
        # Sign the user in.
        auth_user = authenticate(identification=user.email, check_password=False)
        auth_login(request, auth_user)

        if success_url: 
            redirect_to = success_url % {'username': user.username }
        else: 
            redirect_to = reverse('accounts_profile_detail', kwargs={'username': user.username})
        return redirect(redirect_to)
    else:
        if not extra_context: 
            extra_context = dict()
        return direct_to_template(request, template_name, extra_context=extra_context)

@secure_required
def email_change(request, email_form=EmailForm,
                 template_name='accounts/email_change_form.html', success_url=None,
                 extra_context=None):
    """
    Change email address

    :param email_form:
        Form that will be used to change the email address. Defaults to
        :class:`EmailForm` supplied by accounts.

    :param template_name:
        String containing the template to be used to display the email form.
        Defaults to ``accounts/email_form.html``.

    :param success_url:
        Named URL where the user will get redirected to when succesfully
        changing their email address.  When not suplied will redirect to
        ``accounts_email_complete`` URL.

    :param extra_context:
        Dictionary containing extra variables that can be used to render the
        template. The ``form`` key is always the form supplied by the keyword
        argument ``form`` and the ``user`` key by the user whose email address
        is being changed.

    **Context**

    ``form``
        Form that is used to change the email address supplied by ``form``.

    ``account``
        Instance of the ``Account`` whose email address is about to be changed.

    **Todo**

    Need to have per-object permissions, which enables users with the correct
    permissions to alter the email address of others.

    """
    user = get_object_or_404(User, username__iexact=request.user.username)

    form = email_form(user)

    if request.method == 'POST':
        form = email_form(user,
                               request.POST,
                               request.FILES)

        if form.is_valid():
            email_result = form.save()

            if success_url: redirect_to = success_url
            else: redirect_to = reverse('accounts_email_change_done',
                                        kwargs={'username': user.username})
            return redirect(redirect_to)

    if not extra_context: extra_context = dict()
    extra_context['form'] = form
    extra_context['profile'] = user.get_profile()
    return direct_to_template(request,
                              template_name,
                              extra_context=extra_context)

@secure_required
def email_confirm(request, confirmation_key,
                  template_name='accounts/email_change_fail.html',
                  success_url=None, extra_context=None):
    """
    Confirms an email address with a confirmation key.

    Confirms a new email address by running :func:`User.objects.confirm_email`
    method. If the method returns an :class:`User` the user will have his new
    e-mail address set and redirected to ``success_url``. If no ``User`` is
    returned the user will be represented with a fail message from
    ``template_name``.

    :param username:
        String of the username whose email address needs to be confirmed.

    :param confirmation_key:
        String with a SHA1 representing the confirmation key used to verify a
        new email address.

    :param template_name:
        String containing the template name which should be rendered when
        confirmation fails. When confirmation is succesfull, no template is
        needed because the user will be redirected to ``success_url``.

    :param success_url:
        String containing the URL which is redirected to after a succesfull
        confirmation.  Supplied argument must be able to be rendered by
        ``reverse`` function.

    :param extra_context:
        Dictionary of variables that are passed on to the template supplied by
        ``template_name``.

    """
    user = Account.objects.confirm_email(confirmation_key)
    if user:
        if success_url: redirect_to = success_url
        else: redirect_to = reverse('accounts_email_change_complete',
                                    kwargs={'username': user.username})
        return redirect(redirect_to)
    else:
        if not extra_context: extra_context = dict()
        return direct_to_template(request,
                                  template_name,
                                  extra_context=extra_context)

@secure_required
def password_change(request, template_name='accounts/password_change_form.html',
                    pass_form=PasswordChangeForm, success_url=None, extra_context=None):
    """ Change password of user.

    This view is almost a mirror of the view supplied in
    :func:`contrib.auth.views.password_change`, with the minor change that in
    this view we also use the username to change the password. This was needed
    to keep our URLs logical (and REST) accross the entire application. And
    that in a later stadium administrators can also change the users password
    through the web application itself.

    :param template_name:
        String of the name of the template that is used to display the password
        change form. Defaults to ``accounts/password_form.html``.

    :param pass_form:
        Form used to change password. Default is the form supplied by Django
        itself named ``PasswordChangeForm``.

    :param success_url:
        Named URL that is passed onto a :func:`reverse` function with
        ``username`` of the active user. Defaults to the
        ``accounts_password_complete`` URL.

    :param extra_context:
        Dictionary of extra variables that are passed on the the template. The
        ``form`` key is always used by the form supplied by ``pass_form``.

    **Context**

    ``form``
        Form used to change the password.

    """
    user = get_object_or_404(User, username__iexact=request.user.username)

    form = pass_form(user=user)

    if request.method == "POST":
        form = pass_form(user=user, data=request.POST)
        if form.is_valid():
            form.save()

            # Send a signal that the password has changed
            accounts_signals.password_complete.send(sender=None,
                                                   user=user)

            if success_url: redirect_to = success_url
            else: redirect_to = reverse('accounts_password_change_complete',
                                        kwargs={'username': user.username})
            return redirect(redirect_to)

    if not extra_context: extra_context = dict()
    extra_context['form'] = form
    extra_context['profile'] = user.get_profile()
    return direct_to_template(request,
                              template_name,
                              extra_context=extra_context)

@secure_required
def account_edit(request, account_form=AccountForm,
                 template_name='accounts/account_edit_form.html', success_url=None,
                 extra_context=None, **kwargs):
    """
    Edit account.

    Edits an account selected by the supplied username. First checks
    permissions if the user is allowed to edit this account, if denied will
    show a 404. When the account is succesfully edited will redirect to
    ``success_url``.

    :param account_form:

        Form that is used to edit the account. The :func:`AccountForm.save`
        method of this form will be called when the form
        :func:`AccountForm.is_valid`.  Defaults to :class:`AccountForm`
        from manifest.accounts.

    :param template_name:
        String of the template that is used to render this view. Defaults to
        ``accounts/account_form.html``.

    :param success_url:
        Named URL which be passed on to a django ``reverse`` function after the
        form is successfully saved. Defaults to the ``accounts_detail`` url.

    :param extra_context:
        Dictionary containing variables that are passed on to the
        ``template_name`` template.  ``form`` key will always be the form used
        to edit the account, and the ``account`` key is always the edited
        account.

    **Context**

    ``form``
        Form that is used to alter the account.

    ``account``
        Instance of the ``Account`` that is edited.

    """
    user = get_object_or_404(User, username__iexact=request.user.username)

    account = user.account

    user_initial = {'first_name': user.first_name,
                    'last_name': user.last_name}

    form = account_form(instance=account, initial=user_initial)

    if request.method == 'POST':
        form = account_form(request.POST, request.FILES, instance=account,
                                 initial=user_initial)
        if form.is_valid():
            account = form.save()

            if accounts_settings.ACCOUNTS_USE_MESSAGES:
                messages.success(request, _('Your account has been updated.'),
                                 fail_silently=True)

            if success_url: redirect_to = success_url
            else: redirect_to = reverse('accounts_profile_detail', kwargs={'username': request.user.username})
            return redirect(redirect_to)

    if not extra_context: extra_context = dict()
    extra_context['form'] = form
    extra_context['account'] = account
    return direct_to_template(request,
                              template_name,
                              extra_context=extra_context,
                              **kwargs)

@secure_required
def profile_edit(request, profile_form=ProfileForm,
                 template_name='accounts/profile_edit_form.html', success_url=None,
                 extra_context=None, **kwargs):
    """
    Edit profile.

    Edits a profile selected by the supplied username. First checks
    permissions if the user is allowed to edit this profile, if denied will
    show a 404. When the profile is succesfully edited will redirect to
    ``success_url``.

    :param profile_form:

        Form that is used to edit the profile. The :func:`ProfileForm.save`
        method of this form will be called when the form
        :func:`ProfileForm.is_valid`.  Defaults to :class:`ProfileForm`
        from manifest.accounts.

    :param template_name:
        String of the template that is used to render this view. Defaults to
        ``accounts/profile_form.html``.

    :param success_url:
        Named URL which be passed on to a django ``reverse`` function after the
        form is successfully saved. Defaults to the ``accounts_detail`` url.

    :param extra_context:
        Dictionary containing variables that are passed on to the
        ``template_name`` template.  ``form`` key will always be the form used
        to edit the profile, and the ``profile`` key is always the edited
        profile.

    **Context**

    ``form``
        Form that is used to alter the profile.

    ``profile``
        Instance of the ``Profile`` that is edited.

    """
    user = get_object_or_404(User, username__iexact=request.user.username)

    profile = user.get_profile()

    user_initial = {'first_name': user.first_name,
                    'last_name': user.last_name}

    form = profile_form(instance=profile, initial=user_initial)

    if request.method == 'POST':
        form = profile_form(request.POST, request.FILES, instance=profile,
                                 initial=user_initial)

        if form.is_valid():
            profile = form.save()

            if accounts_settings.ACCOUNTS_USE_MESSAGES:
                messages.success(request, _('Your profile has been updated.'),
                                 fail_silently=True)

            if success_url: redirect_to = success_url
            else: redirect_to = reverse('accounts_profile_detail', kwargs={'username': username})
            return redirect(redirect_to)

    if not extra_context: extra_context = dict()
    extra_context['form'] = form
    extra_context['profile'] = profile
    return direct_to_template(request,
                              template_name,
                              extra_context=extra_context,
                              **kwargs)

def profile_list(request, page=1, template_name='accounts/profile_list.html',
                 paginate_by=50, extra_context=None, **kwargs):
    """
    Returns a list of all profiles that are public.

    It's possible to disable this by changing ``ACCOUNTS_DISABLE_PROFILE_LIST``
    to ``True`` in your settings.

    :param page:
        Integer of the active page used for pagination. Defaults to the first
        page.

    :param template_name:
        String defining the name of the template that is used to render the
        list of all users. Defaults to ``accounts/list.html``.

    :param paginate_by:
        Integer defining the amount of displayed profiles per page. Defaults to
        50 profiles per page.

    :param extra_context:
        Dictionary of variables that are passed on to the ``template_name``
        template.

    **Context**

    ``profile_list``
        A list of profiles.

    ``is_paginated``
        A boolean representing whether the results are paginated.

    If the result is paginated. It will also contain the following variables.

    ``paginator``
        An instance of ``django.core.paginator.Paginator``.

    ``page_obj``
        An instance of ``django.core.paginator.Page``.

    """
    try:
        page = int(request.GET.get('page', None))
    except (TypeError, ValueError):
        page = page

    if accounts_settings.ACCOUNTS_DISABLE_PROFILE_LIST \
       and not request.user.is_staff:
        raise Http404

    profile_model = get_profile_model()
    queryset = profile_model.objects.all()

    if not extra_context: extra_context = dict()
    return list_detail.object_list(request,
                                   queryset=queryset,
                                   paginate_by=paginate_by,
                                   page=page,
                                   template_name=template_name,
                                   extra_context=extra_context,
                                   template_object_name='profile',
                                   **kwargs)

def profile_detail(
    request, username,
    template_name=accounts_settings.ACCOUNTS_PROFILE_DETAIL_TEMPLATE,
    extra_context=None, **kwargs):
    """
    Detailed view of an user.

    :param username:
        String of the username of which the profile should be viewed.

    :param template_name:
        String representing the template name that should be used to display
        the profile.

    :param extra_context:
        Dictionary of variables which should be supplied to the template. The
        ``profile`` key is always the current profile.

    **Context**

    ``profile``
        Instance of the currently viewed ``Profile``.

    """
    user = get_object_or_404(User, username__iexact=username)
    profile = user.get_profile()
    if not extra_context: extra_context = dict()
    extra_context['profile'] = user.get_profile()
    extra_context['hide_email'] = accounts_settings.ACCOUNTS_HIDE_EMAIL
    return direct_to_template(request,
                              template_name,
                              extra_context=extra_context,
                              **kwargs)

def direct_to_user_template(request, username, template_name,
                            extra_context=None):
    """
    Simple wrapper for Django's :func:`direct_to_template` view.

    This view is used when you want to show a template to a specific user. A
    wrapper for :func:`direct_to_template` where the template also has access to
    the user that is found with ``username``. For ex. used after register,
    activation and confirmation of a new e-mail.

    :param template_name:
        String defining the name of the template to use. Defaults to
        ``accounts/register_complete.html``.

    **Keyword arguments**

    ``extra_context``
        A dictionary containing extra variables that should be passed to the
        rendered template. The ``account`` key is always the ``User``
        that completed the action.

    **Extra context**

    ``viewed_user``
        The currently :class:`User` that is viewed.

    """
    user = get_object_or_404(User, username__iexact=username)

    if not extra_context: extra_context = dict()
    extra_context['viewed_user'] = user
    extra_context['profile'] = user.get_profile()
    return direct_to_template(request,
                              template_name,
                              extra_context=extra_context)
