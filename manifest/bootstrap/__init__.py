from django import template
template.add_to_builtins('django.templatetags.i18n')
template.add_to_builtins('django.contrib.comments.templatetags.comments')
template.add_to_builtins('sorl.thumbnail.templatetags.thumbnail')
template.add_to_builtins('manifest.bootstrap.templatetags.bootstrap_tags')
