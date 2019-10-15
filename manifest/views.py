# -*- coding: utf-8 -*-
""" Manifest Views
"""

from django.contrib.auth import (
    REDIRECT_FIELD_NAME,
    get_user_model,
    login,
    update_session_auth_hash,
)
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.views import LoginView, LogoutView
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)

from manifest import defaults, messages, signals
from manifest.forms import (
    EmailChangeForm,
    LoginForm,
    ProfileUpdateForm,
    RegisterForm,
)
from manifest.mixins import (
    EmailChangeMixin,
    LoginRequiredMixin,
    MessageMixin,
    SecureRequiredMixin,
    SendActivationMailMixin,
    UserFormMixin,
)
from manifest.utils import get_login_redirect


@method_decorator(sensitive_post_parameters("password"), name="dispatch")
class AuthLoginView(LoginView, SecureRequiredMixin, MessageMixin):
    """Authenticate user by email or username with password.

    If the credentials are correct and the user ``is_active``,
    user will be redirected to ``success_url`` if it is defined.

    If ``success_url`` is not defined, the ``login_redirect`` function
    will be called with the arguments ``REDIRECT_FIELD_NAME`` and an
    instance of the ``User`` who is trying the login. The returned
    value of the function will be the URL that will be redirected to.
    """

    form_class = LoginForm
    template_name = "manifest/auth_login.html"
    success_message = messages.AUTH_LOGIN_SUCCESS
    redirect_authenticated_user = True

    def form_valid(self, form):
        user = form.get_user()
        if user.is_active:
            login(self.request, user)
            self.request.session.set_expiry(
                defaults.MANIFEST_REMEMBER_DAYS[1] * 86400
            )
            self.set_success_message(self.success_message)
            if self.success_url:
                return redirect(self.success_url)
            url = get_login_redirect(
                self.request.GET.get(
                    REDIRECT_FIELD_NAME,
                    self.request.POST.get(REDIRECT_FIELD_NAME),
                )
            )
            return redirect(url)
        return redirect(reverse("auth_disabled"))


# pylint: disable=too-many-ancestors
class AuthLogoutView(LogoutView, MessageMixin):
    """Django ``LogoutView`` wrapper.

    Display a success message if ``MANIFEST_USE_MESSAGES`` setting is ``True``
    """

    template_name = "manifest/auth_logout.html"
    success_message = messages.AUTH_LOGOUT_SUCCESS

    def dispatch(self, request, *args, **kwargs):
        self.set_success_message(self.success_message)
        return super().dispatch(request, *args, **kwargs)


# pylint: disable=bad-continuation,too-many-ancestors
@method_decorator(
    sensitive_post_parameters("password1", "password2"), name="dispatch"
)
class AuthRegisterView(
    CreateView, SecureRequiredMixin, MessageMixin, SendActivationMailMixin
):
    """Register user with username, email and password.

    Users receives an email with an activation link to activate their
    account if ``MANIFEST_ACTIVATION_REQUIRED`` setting is ``True``.

    Redirects to ``success_url`` if it is defined, else redirects to
    ``auth_register_complete`` view.
    """

    model = get_user_model()
    form_class = RegisterForm

    template_name = "manifest/auth_register.html"
    success_message = messages.AUTH_REGISTER_SUCCESS
    redirect_authenticated_user = True

    email_subject_template_name = "manifest/emails/activation_email_subject.txt"
    email_message_template_name = "manifest/emails/activation_email_message.txt"

    def dispatch(self, request, *args, **kwargs):
        if self.redirect_authenticated_user and request.user.is_authenticated:
            return redirect(
                get_login_redirect(
                    self.request.GET.get(
                        REDIRECT_FIELD_NAME,
                        self.request.POST.get(REDIRECT_FIELD_NAME),
                    )
                )
            )
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save()
        signals.REGISTRATION_COMPLETE.send(
            sender=None, user=user, request=self.request
        )
        if defaults.MANIFEST_ACTIVATION_REQUIRED:
            self.send_activation_mail(user)

        self.set_success_message(self.success_message)
        if self.success_url:
            return redirect(self.success_url)
        return redirect(reverse("auth_register_complete"))


class AuthActivateView(TemplateView, MessageMixin):
    """Activate the user with the activation token.

    The token is a SHA1 string. When the SHA1 is found with username
    the ``User`` of that account will be activated.

    After a successfull activation user will be redirected to
    ``profile_settings`` view if ``succes_url`` is not defined.

    If the SHA1 is not found, the user will be shown the
    ``template_name`` template that displaying a fail message.
    """

    template_name = "manifest/auth_activate.html"
    success_message = messages.AUTH_ACTIVATE_SUCCESS
    error_message = messages.AUTH_ACTIVATE_ERROR
    success_url = None

    def get_success_url(self, **kwargs):
        if self.success_url:
            return self.success_url % kwargs
        return reverse("profile_settings")

    def get(self, request, *args, **kwargs):
        user = get_user_model().objects.activate_user(
            kwargs["username"], kwargs["token"]
        )
        if user:
            # Sign the user in.
            login(
                request, user, backend="manifest.backends.AuthenticationBackend"
            )
            self.set_success_message(self.success_message)
            return redirect(self.get_success_url(**kwargs))
        self.set_error_message(self.error_message)
        return super().get(request, *args, **kwargs)


class AuthProfileView(DetailView, LoginRequiredMixin):
    """Detail view for current user account

    Simple detail view gets ``request.user`` as object.
    """

    template_name = "manifest/user_detail.html"

    def get_object(self, queryset=None):
        return self.request.user


# pylint: disable=bad-continuation,too-many-ancestors
class ProfileUpdateView(
    UpdateView, SecureRequiredMixin, LoginRequiredMixin, MessageMixin
):
    """Update profile of current user

    Updates profile information for ``request.user``. User will be
    redirected to ``profile_settings`` if ``success_url`` is not defined.
    """

    model = get_user_model()
    form_class = ProfileUpdateForm
    template_name = "manifest/profile_update.html"
    success_message = messages.PROFILE_UPDATE_SUCCESS

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        form.save()
        self.set_success_message(self.success_message)
        if self.success_url:
            return redirect(self.success_url)
        return redirect(reverse("profile_settings"))


class EmailChangeView(UserFormMixin, EmailChangeMixin):
    """Change email of current user

    Changes email for ``request.user``. Change will not be applied
    until user confirm their new email.

    User will be redirected to ``email_change_done`` view
    if ``success_url`` is not defined.
    """

    form_class = EmailChangeForm
    template_name = "manifest/email_change.html"
    success_message = messages.EMAIL_CHANGE_SUCCESS

    def form_valid(self, form):
        user = form.save()
        self.send_confirmation_mail(user)

        self.set_success_message(self.success_message)
        if self.success_url:
            return redirect(self.success_url)
        return redirect(reverse("email_change_done"))


class EmailChangeConfirmView(TemplateView, MessageMixin):
    """Confirm the email address with username and confirmation token.

    Confirms the new email address by running
    ``get_user_model().objects.confirm_email`` method.

    User will be redirected to ``email_change_complete`` view
    if ``success_url`` is not defined.

    If no ``User`` object returned, user will be shown the
    ``template_name`` template that displaying a fail message.
    """

    template_name = "manifest/email_change_confirm.html"
    success_message = messages.EMAIL_CHANGE_CONFIRM_SUCCESS
    error_message = messages.EMAIL_CHANGE_CONFIRM_ERROR
    success_url = None

    def get_success_url(self, **kwargs):
        if self.success_url:
            return self.success_url % kwargs
        return reverse("email_change_complete")

    def get(self, request, *args, **kwargs):
        user = get_user_model().objects.confirm_email(
            kwargs["username"], kwargs["token"]
        )
        if user:
            self.set_success_message(self.success_message)
            return redirect(self.get_success_url(**kwargs))
        self.set_error_message(self.error_message)
        return super().get(request, *args, **kwargs)


@method_decorator(sensitive_post_parameters(), name="dispatch")
class PasswordChangeView(UserFormMixin):
    """Change password of current user.

    Changes password for ``request.user``. User will be redirected to
    ``password_change_done`` view if ``success_url`` is not defined.
    """

    form_class = PasswordChangeForm
    template_name = "manifest/password_change.html"
    success_message = messages.PASSWORD_CHANGE_SUCCESS

    def form_valid(self, form):
        user = form.save()
        signals.PASSWORD_RESET_COMPLETE.send(sender=None, user=user)
        self.set_success_message(self.success_message)
        update_session_auth_hash(self.request, user)
        if self.success_url:
            return redirect(self.success_url)
        return redirect(reverse("password_change_done"))


class UserListView(ListView):
    """Lists active user profiles.

    List view that lists active user profiles
    if ``MANIFEST_DISABLE_PROFILE_LIST`` setting is ``False``,
    else raises Http404.
    """

    queryset = get_user_model().objects.get_visible_profiles()
    template_name = "manifest/user_list.html"
    paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
        if (
            defaults.MANIFEST_DISABLE_PROFILE_LIST
            and not request.user.is_superuser
        ):
            raise Http404
        return super().dispatch(request, *args, **kwargs)


class UserDetailView(DetailView):
    """Displays an active user profile by username.

    Detail view that displays an active user profile by username.
    if ``MANIFEST_DISABLE_PROFILE_LIST`` setting is ``False``,
    else raises Http404.
    """

    queryset = get_user_model().objects.get_visible_profiles()
    template_name = "manifest/user_detail.html"
    slug_field = "username"
    slug_url_kwarg = "username"

    def dispatch(self, request, *args, **kwargs):
        if (
            defaults.MANIFEST_DISABLE_PROFILE_LIST
            and not request.user.is_superuser
        ):
            raise Http404
        return super().dispatch(request, *args, **kwargs)
