# -*- coding: utf-8 -*-
""" Manifest Test Cases
"""
import json
import logging
import tempfile
from contextlib import contextmanager

import django
from django.conf import settings
from django.template import Context, Template
from django.test import RequestFactory, TestCase
from django.test.utils import (
    _TestState,
    setup_databases,
    setup_test_environment,
)
from django.urls import reverse
from django.utils.translation import activate, deactivate

from PIL import Image
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.test import APIClient

from manifest import defaults

TEMPFILE_MEDIA_ROOT = tempfile.mkdtemp()

# If test are not run by Django test runner (eg. IDE),
# setup Django and test environment.
if not hasattr(_TestState, "saved_data"):
    django.setup()
    setup_test_environment()
    setup_databases(1, False)


class ManifestTestCase(TestCase):
    """Base test case that setup fixtures and user locale.
    """

    fixtures = ["test"]
    logger = logging.getLogger(__name__)

    def _pre_setup(self):
        activate(settings.LANGUAGE_CODE)
        super()._pre_setup()

    def setUp(self):
        self.factory = RequestFactory()
        super().setUp()

    def _post_teardown(self):
        super()._post_teardown()
        deactivate()

    # pylint: disable=no-self-use
    def render(self, string, context=None):
        """Renders any given string to template.

        :param string: Template code to render.
        :type string: string
        :param context: Template context to be rendered, defaults to None
        :type context: dict, optional
        :return: Rendered template.
        :rtype: string
        """
        context = context or {}
        context = Context(context)
        return Template(string).render(context)

    @contextmanager
    def defaults(self, **kwargs):
        original = {}
        for key, value in kwargs.items():
            original[key] = getattr(defaults, key, None)
            setattr(defaults, key, value)
        yield
        for key, value in original.items():
            setattr(defaults, key, value)


class ManifestAPIClient(APIClient):
    """Test client for REST API tests.
    """

    def login(self, **credentials):
        super(ManifestAPIClient, self).login(**credentials)
        try:
            response = self.post(reverse("auth_login_api"), data=credentials)
            self.credentials(
                HTTP_AUTHORIZATION="JWT " + response.json["token"]
            )
        except KeyError:
            AuthenticationFailed("No Token")

    # pylint: disable=bad-continuation,too-many-arguments
    def generic(
        self,
        method,
        path,
        data="",
        content_type="application/json",
        secure=False,
        **extra,
    ):
        response = super().generic(
            method, path, data, content_type, secure, **extra
        )
        try:
            is_json = bool(
                # pylint: disable=W0212
                [x for x in response._headers["content-type"] if "json" in x]
            )
        except KeyError:
            is_json = False

        response.json = {}
        if is_json and response.content:
            response.json = json.loads(response.content)

        return response


class ManifestAPITestCase(ManifestTestCase):
    """Test case for REST API views.
    """

    client_class = ManifestAPIClient


class ManifestUploadTestCase(ManifestTestCase):
    """Test case for image uploading views.
    """

    # pylint: disable=no-self-use
    def create_image(self, suffix=".png", image_format="PNG"):
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as file:
            image = Image.new("RGB", (200, 200), "white")
            image.save(file, image_format)
        return file

    def get_file(self, file):
        return open(file.name, mode="rb")

    # pylint: disable=no-self-use
    def get_raw_file(self, file):
        from django.core.files.uploadedfile import SimpleUploadedFile

        return SimpleUploadedFile(
            name=file.name,
            content=open(file.name, "rb").read(),
            content_type="image/png",
        )

    def setUp(self):
        self.image_file = self.get_file(self.create_image())
        self.raw_image_file = self.get_raw_file(self.image_file)
        super().setUp()

    def tearDown(self):
        self.image_file.close()
        self.raw_image_file.close()

    @contextmanager
    def upload_limit(self):
        old = defaults.MANIFEST_PICTURE_MAX_FILE
        defaults.MANIFEST_PICTURE_MAX_FILE = 1
        yield
        defaults.MANIFEST_PICTURE_MAX_FILE = old
