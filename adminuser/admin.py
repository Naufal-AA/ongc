from django.contrib import admin
from .models import *


# Register your models here.
class storySettings(admin.ModelAdmin):
    list_display = [field.name for field in Stories._meta.get_fields()]
    
class newsSettings(admin.ModelAdmin):
    list_display = [field.name for field in News._meta.get_fields()]

admin.site.register(Stories, storySettings)
admin.site.register(News, newsSettings)