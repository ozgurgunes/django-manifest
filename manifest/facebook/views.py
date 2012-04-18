import urllib
from django.http import HttpResponse
from django.contrib.auth import authenticate
from django.shortcuts import redirect
from django.utils import simplejson as json

from social_auth.backends import get_backend
from social_auth.backends.facebook import FacebookAuth
from manifest.facebook.api import Graph

def connect(request, *args, **kwargs):    
    access_token = request.GET.get('access_token')
    redirect_url = request.GET.get('redirect')

    url = ACCESS_TOKEN + urlencode({
        'client_id': setting('FACEBOOK_APP_ID'),
        'redirect_uri': self.redirect_uri,
        'client_secret': setting('FACEBOOK_API_SECRET'),
        'code': self.data['code']
    })
    
    facebook = get_backend('facebook', request, None)
    data = facebook.user_data(access_token)
    
    if not data:
        return HttpResponse('FAIL')

    kwargs.update({
        'auth': facebook,
        'response': data,
        'facebook': True
        })
    
    authenticate(*args, **kwargs)
    return redirect(redirect_url)

def post(request, path, *args, **kwargs):
    facebook = Graph(request.user)
    params = {
        "message":  "Post message",
        "link"   : "http://www.facebook.com/pages/Propaganda-Test/335920636447614?sk=app_407776845917666",
        "caption" : "Mooudunu sec videonu izle",
        "picture":  "http://img.youtube.com/vi/316AzLYfAzw/0.jpg",
        "source":   "http://www.youtube.com/e/316AzLYfAzw",
        #"name"   : "Facebook wall post",
        #"description": "Lorem ipsum dolor sit amet",
        #"tags": "mood, freemod",
    }
    response = facebook.post(path, params)
    return HttpResponse(response)
