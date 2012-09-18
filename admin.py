from django.contrib import admin
from bolti.models import Practice

class PracticeAdmin(admin.ModelAdmin):
    fields=['dt']
    
admin.site.register(Practice, PracticeAdmin)