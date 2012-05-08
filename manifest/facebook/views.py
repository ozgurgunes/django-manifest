# -*- coding: utf-8 -*-
from django.conf import settings
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt
from manifest.facebook.utils import parse_signed_request

@csrf_exempt
def iframe(request, 
        liked_template='facebook/iframe_liked.html', 
        unliked_template='facebook/iframe_unliked.html',
        extra_context={}, *args, **kwargs):
    """
    Generic view for facebook iframe tabs and canvases
    
    Provides a view for Facebook iframe applications and page tabs. 
    Parses Facebook's signed_request and renders a template depends on like data. 
    
    :param liked_template:
        String defining the name of the template if user liked the Facebook Page.
        Default is ``facebook/iframe_liked.html``.

    :param unliked_template:
        String defining the name of the template if user has not liked the Facebook Page yet.
        Default is ``facebook/iframe_unliked.html``.

    :param extra_context:
        A dictionary containing extra variables that should be passed to the
        rendered template.
        
    """
    signed_request = parse_signed_request(request.POST.get('signed_request'), settings.FACEBOOK_API_SECRET)
    if signed_request:
        request.session['liked'] = signed_request['page']['liked']
    liked = request.session.get('liked', False)
    template = liked_template if liked else unliked_template
    extra_context.update({'liked': liked})
    return render_to_response(template, extra_context, context_instance=RequestContext(request))