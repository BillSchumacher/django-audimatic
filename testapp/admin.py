from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from testapp.models import CustomUser, UserAuditTrail

admin.site.register(UserAuditTrail, admin.ModelAdmin)
admin.site.register(CustomUser, UserAdmin)
