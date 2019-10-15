# -*- coding: utf-8 -*-
""" Manifest Template Tests
"""

from django.urls import reverse

from manifest import forms
from tests.base import ManifestTestCase


class TemplateTests(ManifestTestCase):
    """Tests for templates used by various views and errors.
    """

    def test_page_not_found(self):
        """
        A ``GET`` to the view should render the correct form.
        """
        response = self.client.get(reverse("page_not_found"))
        self.assertTemplateUsed(response, "404.html")

    def test_server_error(self):
        """
        A ``GET`` to the view should render the correct form.
        """
        response = self.client.get(reverse("server_error"))
        self.assertTemplateUsed(response, "500.html")

    def test_homepage(self):
        """
        A ``GET`` to the view should render the correct form.
        """
        response = self.client.get(reverse("homepage"))
        self.assertTemplateUsed(response, "homepage.html")

    def test_flatpage(self):
        """
        A ``GET`` to the view should render the correct form.
        """
        response = self.client.get("/flatpages/flatpage-url/")
        self.assertTemplateUsed(response, "flatpages/default.html")


class TemplatetagTests(ManifestTestCase):
    """Tests for :mod:`manifest <manifest.templatetags.manifest>` templatetags.
    """
    def test_active_nav_path(self):
        """Should return active if request is at given path.
        """
        request = self.factory.get(reverse("homepage"))
        render = self.render("{% active_nav '/' %}", {"request": request})
        self.assertEqual(render, "active")

    def test_active_nav_url(self):
        """Should return active if request is at given url.
        """
        request = self.factory.get(reverse("homepage"))
        render = self.render(
            "{% active_nav 'homepage' %}", {"request": request}
        )
        self.assertEqual(render, "active")

    def test_form(self):
        """Should render form.
        """
        form = forms.RegisterForm
        self.assertRaises(
            AttributeError,
            self.render,
            "{{ form|bootstrap_form }}",
            {"form": {}},
        )
        render = self.render(
            "{% load manifest %}{{ form|bootstrap_form }}", {"form": form}
        )
        self.assertTrue("<input" in render)

    def test_formset(self):
        """Should render formset.
        """
        from django.forms import formset_factory

        form = formset_factory(forms.RegisterForm)
        render = self.render(
            "{% load manifest %}{{ form|bootstrap_form }}", {"form": form}
        )
        self.assertTrue("form-TOTAL_FORMS" in render)


class ContextProcessorTests(ManifestTestCase):
    """Tests for :mod:`context_processors <manifest.context_processors>`.
    """

    def test_site(self):
        response = self.client.get(reverse("homepage"))
        self.assertTrue("site" in response.context)

    def test_installed_apps(self):
        response = self.client.get(reverse("homepage"))
        self.assertTrue("INSTALLED_APPS" in response.context)

    def test_messages(self):
        response = self.client.get(reverse("homepage"))
        self.assertTrue("MANIFEST_USE_MESSAGES" in response.context)

    def test_remote_addr(self):
        response = self.client.get(reverse("homepage"))
        self.assertTrue("user_ip" in response.context)
