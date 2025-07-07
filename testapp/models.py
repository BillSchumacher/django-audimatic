from django.contrib.auth.models import AbstractUser
from django.db import models

from django_audimatic.models import AuditTrail, AuditTrigger


class UserAuditTrail(AuditTrail):
    pass


class CustomUser(AbstractUser, AuditTrigger):
    class Meta(AuditTrigger.Meta):
        audit_table = UserAuditTrail


class ProjectAuditTrail(AuditTrail):
    pass


class Project(AuditTrigger):
    name = models.CharField(max_length=128)
    members = models.ManyToManyField(CustomUser)

    class Meta(AuditTrigger.Meta):
        audit_table = ProjectAuditTrail
        audit_options = {'track_m2m': True}
