from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from django_audimatic.admin import DiffInline
from testapp.models import CustomUser, UserAuditTrail


class CustomUserAuditTrail(DiffInline):
    model = CustomUser.get_audit_table()


class CustomUserAdmin(UserAdmin):
    inlines = (CustomUserAuditTrail,)


admin.site.register(UserAuditTrail, admin.ModelAdmin)
admin.site.register(CustomUser, CustomUserAdmin)
