from manifest.profiles.models import Profile, ServiceType, Service, Link
from django.contrib import admin

class ServiceInline(admin.TabularInline):
    model = Service
    extra = 3

class LinkInline(admin.TabularInline):
    model = Link
    extra = 3
    
class ProfileAdmin(admin.ModelAdmin):
    list_display    = ('user', 'gender', 'birth_date')
    list_filter     = ['user']
    search_fields   = ['user']
    inlines         = [ServiceInline, LinkInline]
admin.site.register(Profile, ProfileAdmin)

class ServiceTypeAdmin(admin.ModelAdmin):
    list_display    = ('title', 'url')
    list_filter     = ['title']
    search_fields   = ['title']
admin.site.register(ServiceType, ServiceTypeAdmin)