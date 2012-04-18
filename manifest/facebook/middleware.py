# -*- coding: utf8 -*-

class FacebookMiddleware(object):
    
    def process_response(self, request, response):
        """
        internet explorer fix for iframe typed facebook applications.
        """
        response['P3P'] = 'CP="NOI DSP COR NID ADMa OPTa OUR NOR"'
        return response 
        