from setuptools import setup, find_packages
import re

# Dynamically calculate the version based on manifest.VERSION.
version = __import__('manifest').get_version()

def parse_requirements(file_name):
    requirements = []
    for line in open(file_name, 'r').read().split('\n'):
        if re.match(r'(\s*#)|(\s*$)', line):
            continue
        if re.match(r'\s*-e\s+', line):
            requirements.append(re.sub(r'\s*-e\s+.*#egg=(.*)$', r'\1', line))
        elif re.match(r'\s*-f\s+', line):
            pass
        else:
            requirements.append(line)

    return requirements

def parse_dependency_links(file_name):
    dependency_links = []
    for line in open(file_name, 'r').read().split('\n'):
        if re.match(r'\s*-[ef]\s+', line):
            dependency_links.append(re.sub(r'\s*-[ef]\s+', '', line))

    return dependency_links
    
setup(
    name="django-manifest",
    version=version,
    description = "A package to help automate creation of web applications in Django",
    long_description=open("README").read(),
    author = "Propaganda Istanbul",
    author_email = "developer@propaganda.com.tr",
    url = "http://github.com/propaganda-istanbul/django-manifest/",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 1 - Planning",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Framework :: Django",
    ],
    include_package_data=True,
    zip_safe=False,
    entry_points={
            "console_scripts": [
                "manifest-admin = manifest.core.management:execute_from_command_line",
            ],
        },
)
