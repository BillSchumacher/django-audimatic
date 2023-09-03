from django.contrib.auth.models import AbstractUser

from django_audimatic.models import AuditTrail, AuditTrigger


class UserAuditTrail(AuditTrail):
    pass


class CustomUser(AbstractUser, AuditTrigger):
    class Meta(AuditTrigger.Meta):
        audit_table = UserAuditTrail
