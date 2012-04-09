from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.generic.list_detail import object_list
from django.core.urlresolvers import reverse

from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import comments

from manifest.profiles import utils, forms
from manifest.profiles.models import Profile

from relationships.models import Relationship

@login_required
def profile_settings(request, template_name='profiles/profile_settings.html'):
    return render_to_response(template_name, { 'user': request.user, 'object': request.user.get_profile() }, context_instance=RequestContext(request))

@login_required
def profile_edit(request, context={}, form=forms.ProfileForm, template_name='profiles/profile_form.html'):
    """Edit profile."""
    profile = get_object_or_404(Profile, user=request.user.id)
    context['object'] = profile
    if request.POST:
        form = form(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('profiles_profile_detail', kwargs={'username': request.user.username}))
        else:
            context['form'] = form
    else:
        context['form'] = form(instance=profile)
    return render_to_response(template_name, context, context_instance=RequestContext(request))

@login_required
def mugshot_upload(request, context={}, form=forms.MugshotForm, template_name='profiles/profile_form_mugshot.html'):
    """
    Upload mugshot
    
    """
    profile = get_object_or_404(Profile, user=request.user)
    context['object'] = profile
    if request.POST:
        form = form(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('profiles_profile_detail', kwargs={'username': request.user.username}))
        else:
            context['form'] = form
    else:
        context['form'] = form(instance=profile)
    return render_to_response(template_name, context, context_instance=RequestContext(request))

def profile_detail(request, username, public_profile_field=None,
                   template_name='profiles/profile_detail.html',
                   extra_context=None):
    """
    Detail view of a user's profile.
    
    If no profile model has been specified in the
    ``AUTH_PROFILE_MODULE`` setting,
    ``django.contrib.auth.models.SiteProfileNotAvailable`` will be
    raised.
    
    If the user has not yet created a profile, ``Http404`` will be
    raised.
    
    **Required arguments:**
    
    ``username``
        The username of the user whose profile is being displayed.
    
    **Optional arguments:**

    ``extra_context``
        A dictionary of variables to add to the template context. Any
        callable object in this dictionary will be called to produce
        the end result which appears in the context.

    ``public_profile_field``
        The name of a ``BooleanField`` on the profile model; if the
        value of that field on the user's profile is ``False``, the
        ``profile`` variable in the template will be ``None``. Use
        this feature to allow users to mark their profiles as not
        being publicly viewable.
        
        If this argument is not specified, it will be assumed that all
        users' profiles are publicly viewable.
    
    ``template_name``
        The name of the template to use for displaying the profile. If
        not specified, this will default to
        :template:`profiles/profile_detail.html`.
    
    **Context:**
    
    ``profile``
        The user's profile, or ``None`` if the user's profile is not
        publicly viewable (see the description of
        ``public_profile_field`` above).
    
    **Template:**
    
    ``template_name`` keyword argument or
    :template:`profiles/profile_detail.html`.
    
    """
    from utils import get_labels_for_model

    try:
        user = User.objects.get(username=username)
        profile_obj = user.get_profile()
    except ObjectDoesNotExist:
        raise Http404
    if public_profile_field is not None and \
       not getattr(profile_obj, public_profile_field):
        profile_obj = None
    
    if extra_context is None:
        extra_context = {}
    context = RequestContext(request)
    for key, value in extra_context.items():
        context[key] = callable(value) and value() or value
    return render_to_response(template_name,
                              { 'object': profile_obj, 'profile_labels': get_labels_for_model(Profile) },
                              context_instance=context)

def profile_list(request, public_profile_field=None,
                 template_name='profiles/profile_list.html', **kwargs):
    """
    A list of user apps.profiles.
    
    If no profile model has been specified in the
    ``AUTH_PROFILE_MODULE`` setting,
    ``django.contrib.auth.models.SiteProfileNotAvailable`` will be
    raised.

    **Optional arguments:**

    ``public_profile_field``
        The name of a ``BooleanField`` on the profile model; if the
        value of that field on a user's profile is ``False``, that
        profile will be excluded from the list. Use this feature to
        allow users to mark their profiles as not being publicly
        viewable.
        
        If this argument is not specified, it will be assumed that all
        users' profiles are publicly viewable.
    
    ``template_name``
        The name of the template to use for displaying the apps.profiles. If
        not specified, this will default to
        :template:`profiles/profile_list.html`.

    Additionally, all arguments accepted by the
    :view:`django.views.generic.list_detail.object_list` generic view
    will be accepted here, and applied in the same fashion, with one
    exception: ``queryset`` will always be the ``QuerySet`` of the
    model specified by the ``AUTH_PROFILE_MODULE`` setting, optionally
    filtered to remove non-publicly-viewable proiles.
    
    **Context:**
    
    Same as the :view:`django.views.generic.list_detail.object_list`
    generic view.
    
    **Template:**
    
    ``template_name`` keyword argument or
    :template:`profiles/profile_list.html`.
    
    """
    profile_model = utils.get_profile_model()
    queryset = profile_model._default_manager.all()
    if public_profile_field is not None:
        queryset = queryset.filter(**{ public_profile_field: True })
    kwargs['queryset'] = queryset
    return object_list(request, template_name=template_name, **kwargs)

def comment_list(request, username, template_name='profiles/comment_list.html', **kwargs):
    try:
        user = User.objects.get(username=username)
        profile_obj = user.get_profile()
    except ObjectDoesNotExist:
        raise Http404
    kwargs['paginate_by'] = 10
    kwargs['extra_context'] = { 'object': profile_obj }
    return object_list(request, template_name=template_name, **kwargs)

def friend_list(request, username, template_name='profiles/friend_list.html', **kwargs):
    try:
        user = User.objects.get(username=username)
        profile_obj = user.get_profile()
        queryset = Relationship.objects.friends(user)
    except ObjectDoesNotExist:
        raise Http404
    kwargs['queryset'] = queryset
    kwargs['paginate_by'] = 10
    kwargs['extra_context'] = { 'object': profile_obj }
    return object_list(request, template_name=template_name, **kwargs)
