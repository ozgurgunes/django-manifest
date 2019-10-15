# -*- coding: utf-8 -*-
""" Django Manifest

Code used in project is mostly taken from
several other open source projects, such as;
Django: https://github.com/django/django
django-rest-framework: https://github.com/encode/django-rest-framework
django-rest-auth: https://github.com/Tivix/django-rest-auth
django-userena-ce: https://github.com/django-userena-ce/django-userena-ce
and others...
"""

from os import path

from setuptools import find_packages, setup

setup(
    name="django-manifest",
    version="0.2.1",
    description="A kickstarter for Django Web Framework projects that supports both legacy frontend and javascript technolohies using REST API.",  # noqa # pylint: disable=line-too-long
    long_description=open(
        path.join(path.dirname(path.abspath(__file__)), "README.md")
    ).read(),
    long_description_content_type='text/markdown',
    author="Özgür Güneş",
    author_email="o.gunes@gmail.com",
    url="http://github.com/ozgurgunes/django-manifest/",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Framework :: Django",
        "Framework :: Django :: 2.2",
        "Topic :: Internet",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Browsers",
        "Topic :: Internet :: WWW/HTTP :: Session",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    include_package_data=True,
    zip_safe=False,
)
