# -*- coding: utf8 -*-
import base64
import hmac
import hashlib
from django.utils import simplejson
from django.conf import settings
from django.http import HttpResponseRedirect

def facebook_required(function):
    """
    facebook_required decorator for views.
    """
    def wrap(request, *args, **kwargs):
        if not request.user.social_auth.get(provider='facebook').extra_data['access_token']:
            return HttpResponseRedirect(settings.LOGIN_URL)
        return function(request, *args, **kwargs)
    return wrap

def base64_url_decode(inp):
    """
    Cleans a base64 encoded string and returns
    it decoded
    """
    padding_factor = (4 - len(inp) % 4) % 4
    inp += "="*padding_factor
    return base64.b64decode(unicode(inp).translate(dict(zip(map(ord, u'-_'), u'+/'))))

def parse_signed_request(signed_request, secret):
    """
    Check if the received signed_request is really coming
    from Facebook using your app secret key.
    Returns a dict containing facebook data or None if it fails.
    """
    if signed_request:
        l = signed_request.split('.', 2)
        encoded_sig = l[0]
        payload = l[1]
        
        sig = base64_url_decode(encoded_sig)
        data = simplejson.loads(base64_url_decode(payload))
        
        if data.get('algorithm').upper() != 'HMAC-SHA256':
            return None
        else:
            expected_sig = hmac.new(secret,
                msg=payload, digestmod=hashlib.sha256).digest()
              
        if sig != expected_sig:
            return None
        else:
            return data
    return False

