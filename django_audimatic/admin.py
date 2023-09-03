from django.contrib import admin
from django.contrib.postgres.fields import HStoreField
from django.db.models import ExpressionWrapper, F
from nonrelated_inlines.admin import NonrelatedStackedInline

from django_audimatic.models import AuditTrigger


class DiffInline(NonrelatedStackedInline):
    fields = ["audit_report"]
    readonly_fields = ["audit_report"]
    max_num = 0
    can_delete = False

    @admin.display(description="Diff")
    def audit_report(self, instance):
        return instance.diff

    def get_form_queryset(self, obj: AuditTrigger):
        return (
            (
                self.model.objects.filter(before__id__contains=obj.id)
                | self.model.objects.filter(after__id__contains=obj.id)
            )
            .annotate(
                diff=ExpressionWrapper(
                    F("after") - F("before"), output_field=HStoreField()
                )
            )
            .all()
        )

    def save_new_instance(self, parent, instance):
        raise NotImplementedError("Saving is done via postgresql triggers.")
