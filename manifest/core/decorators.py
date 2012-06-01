# -*- coding: utf-8 -*-
from functools import wraps
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.utils.decorators import available_attrs

def owner_required(Model=None):
    """
    Usage:
    
    @owner_required(Entry)
    def manage_entry(request, pk=None, object=None):
    
    @owner_required()
    def entry_delete(*args, **kwargs):
        kwargs["post_delete_redirect"] = reverse('manage_blogs')
        return delete_object(*args, **kwargs)
    """
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            user = request.user
            grant = False
            model = Model
            mod_edit = False
            if 'pk' in kwargs:
                pk = int(kwargs['pk'])
                if model:
                    mod_edit = True
                elif 'model' in kwargs:
                    model = kwargs['model']
                object = get_object_or_404(model, pk=pk)                
                if user.is_superuser:
                    grant = True
                else:
                    if user.__class__ == model:
                        grant = pk == user.id
                    else:
                        names = [rel.get_accessor_name() 
                                    for rel 
                                    in user._meta.get_all_related_objects() 
                                    if rel.model == model]
                        if names:
                            grant = pk in [o.id 
                                            for o 
                                            in getattr(user, names[0]).all()]
                if not grant:
                    return HttpResponseForbidden('Forbidden')
                if mod_edit:
                    kwargs['object'] = object
            return view_func(request, *args, **kwargs)
        return wraps(view_func)(_wrapped_view)
    return decorator
