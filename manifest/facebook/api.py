# -*- coding: utf-8 -*-
import urllib
import json


class GraphException(Exception):
    """
    Custom exception class for graph api response errors.
    
    """
    def __init__(self, type, message):
        Exception.__init__(self, message)
        self.type = type
        
class Graph(object):
    """
    Facebook Graph API Backend for the Facebook. 
    """
    
    def __init__(self, user):
        self.access_token = user.facebook_token

    @property
    def access_status(self):
        if not self.access_token:
            return False        
        return True

    def get(self, path, params = None):
        """
        Gets the given object from Facebook.

        Makes a HTTP (GET) request to the facebook graph api servers for given 
        parameters. (just for the information getter methods.)
        
        """
        parameters = {}
        
        if self.access_status:
            parameters.update({'access_token': self.access_token})
        
        if params:
            parameters.update(params)

        response = urllib.urlopen("https://graph.facebook.com/me/%s?%s" % 
                                        (path, urllib.urlencode(parameters)))
        self._handle_errors(response)        
        
        data = json.loads(response.read())
        return data.get('data')
        

    def post(self, path, params):
        """
        makes a HTTP (POST) request to the facebook graph api servers for 
        given parameters. (just for the information setter methods.)
        
        """
        params.update({
            "access_token": self.access_token,
        })

        if params:
            for key, value in params.iteritems():
                if isinstance(value, unicode): 
                    params[key] = value.encode("utf8") 
        params = urllib.urlencode(params)
        
        response = urllib.urlopen("https://graph.facebook.com/%s" % 
                                        path, params)
        self._handle_errors(response)
        
        data = json.loads(response.read())        
        return data
        
    def _handle_errors(self, response):
        """
        handles api-response errors
        """
        if isinstance(response, dict) and response.has_key("error"):
            raise GraphException(api_response["error"]["type"], 
                                    api_response["error"]["message"])
        