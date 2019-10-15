# -*- coding: utf-8 -*-
""" REST API Views
"""

from django.conf import settings
from django.contrib.auth import (
    get_user_model,
    login as django_login,
    logout as django_logout,
)
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ObjectDoesNotExist
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters

from rest_framework import status
from rest_framework.generics import (
    CreateAPIView,
    GenericAPIView,
    ListAPIView,
    RetrieveAPIView,
    RetrieveUpdateAPIView,
)
from rest_framework.parsers import FormParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from manifest import defaults, messages, serializers
from manifest.mixins import EmailChangeMixin, SendActivationMailMixin
from manifest.signals import REGISTRATION_COMPLETE
from manifest.utils import jwt_encode


@method_decorator(sensitive_post_parameters("password"), name="dispatch")
class AuthLoginAPIView(GenericAPIView):
    """Check credentials, authenticate and return JWT Token
    if credentials are valid.
    """

    permission_classes = (AllowAny,)
    serializer_class = serializers.LoginSerializer
    token_serializer = serializers.JWTSerializer
    success_message = messages.AUTH_LOGIN_SUCCESS

    user = token = request = serializer = None

    def login(self):
        self.user = self.serializer.validated_data["user"]
        self.token = jwt_encode(self.user)
        if getattr(settings, "REST_SESSION_LOGIN", True):
            django_login(self.request, self.user)

    def get_response(self):
        serializer_class = self.token_serializer
        data = {
            "detail": self.success_message,
            "user": self.user,
            "token": self.token,
        }
        serializer = serializer_class(
            instance=data, context={"request": self.request}
        )
        response = Response(serializer.data, status=status.HTTP_200_OK)
        return response

    def post(self, request):
        self.request = request
        self.serializer = self.get_serializer(
            data=self.request.data, context={"request": request}
        )
        self.serializer.is_valid(raise_exception=True)
        self.login()
        return self.get_response()


class AuthLogoutAPIView(APIView):
    """Calls Django logout method and delete the Token object
    assigned to the current User object.

    Accepts/Returns nothing.
    """

    permission_classes = (AllowAny,)
    success_message = messages.AUTH_LOGOUT_SUCCESS

    def get(self, request, *args, **kwargs):
        if getattr(defaults, "MANIFEST_LOGOUT_ON_GET", False):
            response = self.logout(request)
        else:
            raise self.http_method_not_allowed(request, *args, **kwargs)

        return self.finalize_response(request, response, *args, **kwargs)

    def post(self, request):
        return self.logout(request)

    def logout(self, request):
        try:
            request.user.auth_token.delete()
        except (AttributeError, ObjectDoesNotExist):
            pass
        if getattr(settings, "REST_SESSION_LOGIN", True):
            django_logout(request)

        response = Response(
            {"detail": self.success_message}, status=status.HTTP_200_OK
        )

        return response


# pylint: disable=bad-continuation,too-many-ancestors
@method_decorator(
    sensitive_post_parameters("password1", "password2"), name="dispatch"
)
class AuthRegisterAPIView(CreateAPIView, SendActivationMailMixin):

    serializer_class = serializers.RegisterSerializer
    permission_classes = (AllowAny,)
    success_message = messages.AUTH_REGISTER_SUCCESS
    email_subject_template_name = "manifest/emails/activation_email_subject.txt"
    email_message_template_name = (
        "manifest/emails/activation_email_message_api.txt"
    )

    def get_response_data(self, user, token):
        data = {"detail": self.success_message, "user": user, "token": token}
        return serializers.JWTSerializer(data).data

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if request.user.is_authenticated:
            return Response(
                {"detail": messages.AUTH_REGISTER_FORBIDDEN},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        REGISTRATION_COMPLETE.send(
            sender=None, user=user, request=self.request
        )
        if defaults.MANIFEST_ACTIVATION_REQUIRED:
            self.send_activation_mail(user)

        headers = self.get_success_headers(serializer.data)
        return Response(
            self.get_response_data(user, jwt_encode(user)),
            status=status.HTTP_201_CREATED,
            headers=headers,
        )


class AuthActivateAPIView(GenericAPIView):
    """Confirm the email address with username and confirmation key.

    Confirms the new email address by running
    ``get_user_model().objects.confirm_email`` method.

    User will be redirected to ``email_change_complete`` view
    if ``success_url`` is not defined.

    If no ``User`` object returned the user will be shown the
    ``template_name`` template displaying a fail message.
    """

    serializer_class = serializers.ActivateSerializer
    permission_classes = (AllowAny,)
    success_message = messages.AUTH_ACTIVATE_SUCCESS
    error_message = messages.AUTH_ACTIVATE_ERROR

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({"detail": self.success_message})


class PasswordResetAPIView(GenericAPIView):
    """Calls Django Auth PasswordResetForm save method.

    Accepts the following POST parameters: email
    Returns the success/fail message.
    """

    serializer_class = serializers.PasswordResetSerializer
    permission_classes = (AllowAny,)
    success_message = messages.PASSWORD_RESET_SUCCESS
    email_subject_template_name = "manifest/emails/password_reset_subject.txt"
    email_body_template_name = "manifest/emails/password_reset_message_api.txt"
    email_html_template_name = None

    def get_email_kwargs(self, request):
        return {
            "request": request,
            "use_https": request.is_secure(),
            "token_generator": default_token_generator,
            "from_email": None,
            "subject_template_name": self.email_subject_template_name,
            "email_template_name": self.email_body_template_name,
            "html_email_template_name": self.email_html_template_name,
            "extra_email_context": None,
        }

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email_kwargs = self.get_email_kwargs(request)
        serializer.reset_form.save(**email_kwargs)
        return Response(
            {"detail": self.success_message}, status=status.HTTP_200_OK
        )


class PasswordResetVerifyAPIView(GenericAPIView):
    """Password reset e-mail link is confirmed, therefore
    this resets the user's password.

    Accepts the following POST parameters:
    token, uid, new_password1, new_password2
    Returns the success/fail message.
    """

    serializer_class = serializers.PasswordResetVerifySerializer
    permission_classes = (AllowAny,)
    success_message = messages.PASSWORD_RESET_VERIFY_SUCCESS

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({"detail": self.success_message})


@method_decorator(sensitive_post_parameters(), name="dispatch")
class PasswordResetConfirmAPIView(GenericAPIView):
    """Password reset e-mail link is confirmed, therefore
    this resets the user's password.

    Accepts the following POST parameters:
    token, uid, new_password1, new_password2
    Returns the success/fail message.
    """

    serializer_class = serializers.PasswordResetConfirmSerializer
    permission_classes = (AllowAny,)
    success_message = messages.PASSWORD_RESET_CONFIRM_SUCCESS

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": self.success_message})


class AuthProfileAPIView(RetrieveUpdateAPIView):
    """Update profile of current user.

    Updates profile information for ``request.user``. User will be
    redirected to ``user`` view in ``success_url`` is not
    defined.
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.AuthProfileSerializer
    success_message = messages.PROFILE_UPDATE_SUCCESS

    def get_object(self):
        return self.request.user

    def put(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": self.success_message})


class ProfileOptionsAPIView(APIView):
    """Responses list of options for choicefields.
    """

    permission_classes = (AllowAny,)
    serializer_class = serializers.ProfileUpdateSerializer
    # queryset = get_user_model().objects.get_visible_profiles()

    # pylint: disable=no-self-use
    def get(self, request, *args, **kwargs):
        # pylint: disable=protected-access
        genders = get_user_model()._meta.get_field("gender").choices
        timezones = get_user_model()._meta.get_field("timezone").choices
        locales = get_user_model()._meta.get_field("locale").choices
        choices = {
            "gender": dict(genders),
            "timezone": dict(timezones),
            "locale": dict(locales),
        }
        # print (choices)
        return Response(choices)


class EmailChangeAPIView(GenericAPIView, EmailChangeMixin):
    """Change email of current user.

    Changes email for ``request.user``. Change will not be applied
    until user confirm their new email.
    """

    serializer_class = serializers.EmailChangeSerializer
    permission_classes = (IsAuthenticated,)
    success_message = messages.EMAIL_CHANGE_SUCCESS

    email_message_template_name_new = (
        "manifest/emails/confirmation_email_message_new_api.txt"
    )

    def post(self, request):
        serializer = self.get_serializer(user=request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        self.send_confirmation_mail(user)

        return Response({"detail": self.success_message})


class EmailChangeConfirmAPIView(GenericAPIView):
    """Confirm the email address with username and confirmation key.

    Confirms the new email address by running
    ``get_user_model().objects.confirm_email`` method.

    User will be redirected to ``email_change_complete`` view
    if ``success_url`` is not defined.

    If no ``User`` object returned the user will be shown the
    ``template_name`` template displaying a fail message.
    """

    serializer_class = serializers.EmailChangeConfirmSerializer
    permission_classes = (AllowAny,)
    success_message = messages.EMAIL_CHANGE_CONFIRM_SUCCESS
    error_message = messages.EMAIL_CHANGE_CONFIRM_ERROR

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({"detail": self.success_message})


class PictureUploadAPIView(GenericAPIView):
    """Upload profile picture.
    """

    serializer_class = serializers.PictureUploadSerializer
    permission_classes = (IsAuthenticated,)
    success_message = messages.PICTURE_UPLOAD_SUCCESS
    parser_class = (FormParser,)

    def post(self, request):
        serializer = self.get_serializer(request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": self.success_message})


@method_decorator(sensitive_post_parameters(), name="dispatch")
class PasswordChangeAPIView(GenericAPIView):
    """Calls Django Auth SetPasswordForm save method.

    Accepts the following POST parameters: new_password1, new_password2
    Returns the success/fail message.
    """

    serializer_class = serializers.PasswordChangeSerializer
    permission_classes = (IsAuthenticated,)
    success_message = messages.PASSWORD_CHANGE_SUCCESS

    def patch(self, request):
        serializer = self.get_serializer(user=request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": self.success_message})


class UserListAPIView(ListAPIView):
    """Lists active user profiles, accepts ``GET``.

    List view that lists active user profiles
    if ``MANIFEST_DISABLE_PROFILE_LIST`` setting is ``False``,
    else raises Http404.
    """

    serializer_class = serializers.UserSerializer
    permission_classes = (AllowAny,)
    queryset = get_user_model().objects.get_visible_profiles()

    def get(self, request, *args, **kwargs):
        # pylint: disable=bad-continuation
        if (
            defaults.MANIFEST_DISABLE_PROFILE_LIST
            and not request.user.is_superuser
        ):
            return Response(status=status.HTTP_404_NOT_FOUND)
        return super().get(request, *args, **kwargs)


class UserDetailAPIView(RetrieveAPIView):
    """Reads an active user profile by username, accepts ``GET``.

    Detail view that reads an active user profile by username,
    if ``MANIFEST_DISABLE_PROFILE_LIST`` setting is ``False``,
    else raises Http404.
    """

    serializer_class = serializers.UserSerializer
    permission_classes = (AllowAny,)
    queryset = get_user_model().objects.get_visible_profiles()
    lookup_field = "username"
    lookup_url_kwarg = "username"

    def get(self, request, *args, **kwargs):
        # pylint: disable=bad-continuation
        if (
            defaults.MANIFEST_DISABLE_PROFILE_LIST
            and not request.user.is_superuser
        ):
            return Response(status=status.HTTP_404_NOT_FOUND)
        return super().get(request, *args, **kwargs)
