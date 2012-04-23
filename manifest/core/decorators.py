# -*- coding: utf-8 -*-
from functools import wraps
from django.http import HttpResponseRedirect
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

def make_ajax(view_func):
    def _wrapped_view_func(request, *args, **kwargs):
        response = view_func(request, *args, **kwargs) 
        if 'formhash' in request.GET and isinstance(response, HttpResponseRedirect):
            #situation 3 
            location = response['Location']
            return HttpResponse('<script type="text/javascript">window.parent.location.href="%s"</script>' % location)
        elif 'formhash' in request.GET and  isinstance(response, HttpResponse) and request.method == 'POST':
            #situation 2
            js = """
            <script type="text/javascript">
            $(document).ready(function(){ window.parent.replace_iframe(); })
            </script>
            """
            return HttpResponse(response.content + js)
        else:
            return response
    return wraps(view_func)(_wrapped_view_func)

def permission(permission_tester):
    @wraps(permission_tester)
    def view_decorator(view_function):
        @wraps(view_decorator)
        def decorated_view(request, *args, **kwargs):
            if permission_tester(request, *args, **kwargs):
                view_result = view_function(request, *args, **kwargs)
            else:
                try:
                    request.user.message_set.create(message=_("Sorry, you don't have the necessary permissions to view that page."))
                except: pass
                view_result = HttpResponseRedirect("/")
            return view_result
        return decorated_view
    return view_decorator
    
def owner_required(Model=None):
    """
    Usage:
    
    @permission_required('blogs.change_entry')
    @owner_required(Entry)
    def manage_entry(request, object_id=None, object=None):
    
    @permission_required('blogs.delete_entry')
    @owner_required()
    def entry_delete(*args, **kwargs):
        kwargs["post_delete_redirect"] = reverse('manage_blogs')
        return delete_object(*args, **kwargs)
    """
    def _decorator(viewfunc):
        def _closure(request, *args, **kwargs):
            user = request.user
            grant = False
            model = Model
            mod_edit = False
            if 'object_id' in kwargs:
                object_id = int(kwargs['object_id'])
                if model:
                    mod_edit = True
                elif 'model' in kwargs:
                    model = kwargs['model']
                object = get_object_or_404(model, pk=object_id)
                
                if user.is_superuser:
                    grant = True
                else:
                    if user.__class__ == model:
                        grant = object_id == user.id
                    else:
                        names = [rel.get_accessor_name() for rel in user._meta.get_all_related_objects() if rel.model == model]
                        if names:
                            grant = object_id in [o.id for o in getattr(user, names[0]).all()]
                if not grant:
                    response = render_to_response("403.html", {'object': object}, context_instance=RequestContext(request))
                    response.status_code = 403
                    return response
                if mod_edit:
                    kwargs['object'] = object
                
            response = viewfunc(request, *args, **kwargs)
            return response
        
        return wraps(viewfunc)(_closure)
    return _decorator
    
def owner_or_perm_required(Model=None, perm=None):
    """
    Usage:
    
    @owner_or_perm_required(Post, 'post.can_change')
    def post_delete(request, object_id=None, object=None):
    
    @owner_or_perm_required(Post, 'post.can_change')
    def post_delete(*args, **kwargs):
        kwargs["post_delete_redirect"] = reverse('manage_posts')
        return delete_object(*args, **kwargs)
    """
    def _decorator(viewfunc):
        def _closure(request, *args, **kwargs):
            user = request.user
            grant = False
            model = Model
            mod_edit = False
            if 'object_id' in kwargs:
                object_id = int(kwargs['object_id'])
                if model:
                    mod_edit = True
                elif 'model' in kwargs:
                    model = kwargs['model']
                object = get_object_or_404(model, pk=object_id)
                
                if user.is_superuser or (perm and user.has_perm(perm)):
                    grant = True
                else:
                    if user.__class__ == model:
                        grant = object_id == user.id
                    else:
                        names = [rel.get_accessor_name() for rel in user._meta.get_all_related_objects() if rel.model == model]
                        if names:
                            grant = object_id in [o.id for o in getattr(user, names[0]).all()]
                if not grant:
                    response = render_to_response("403.html", {'object': object}, context_instance=RequestContext(request))
                    response.status_code = 403
                    return response
                if mod_edit:
                    kwargs['object'] = object
                
            response = viewfunc(request, *args, **kwargs)
            return response
        
        return wraps(viewfunc)(_closure)
    return _decorator
    
