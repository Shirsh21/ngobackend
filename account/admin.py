from django.contrib import admin
from .models import User, Application
from django.contrib.auth.admin import UserAdmin

# Register your models here.

class Useradmin(UserAdmin):
    list_display=('email','name')
    search_fields = ('email',)
    ordering = ('email',)
    
    filter_horizontal=()
    list_filter=()
    fieldsets=()


admin.site.register(User, Useradmin)

admin.site.register(Application)

# admin.site.register(User)