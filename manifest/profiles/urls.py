from django.conf.urls.defaults import *
from manifest.profiles import views, forms
from relationships import views as relationship_views

urlpatterns = patterns('',

    url(r'settings/$',
        views.profile_settings, dict(template_name='profiles/profile_settings.html'), name='profiles_profile_settings'),
    url(r'^profiles/edit/$',
        views.profile_edit, dict(form=forms.ProfileForm), name='profiles_profile_edit'),
    url(r'^mugshot/edit/$',
        views.mugshot_upload, dict(form=forms.MugshotForm), name='profiles_mugshot_edit'),
    url(r'^services/edit/$',
        views.profile_edit, dict(form=forms.ServiceFormSet, template_name='profiles/profile_formset_services.html'), name='profiles_services_edit'),
    url(r'^links/edit/$',
        views.profile_edit, dict(form=forms.LinkFormSet, template_name='profiles/profile_formset_links.html'), name='profiles_links_edit'),    


    url(r'^(?P<username>\w+)/$', views.profile_detail, name='profiles_profile_detail'),
    url(r'^$', views.profile_list, name='profiles_profiles_list'),
    
)
