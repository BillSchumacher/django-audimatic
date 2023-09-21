"""

"""
from __future__ import annotations

import pgtrigger
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import HStoreField
from django.core import checks
from django.db import models
from django.db.models import ExpressionWrapper, F


class AuditTrail(models.Model):
    """
    An audit trail model mixin, no fields except for a timestamp
    perhaps should be added to tables that utilize this.

    If this data will be accessed frequently consider an IndexedAuditTrail instead.
    """

    before = HStoreField()
    after = HStoreField()

    class Meta:
        abstract = True


class IndexedAuditTrail(models.Model):
    """
    An indexed audit trail model mixin, no fields except for a timestamp
    perhaps should be added to tables that utilize this.
    """

    before = HStoreField(db_index=True)
    after = HStoreField(db_index=True)

    class Meta:
        abstract = True


TRIGGER_SQL = """
    INSERT INTO {meta.audit_table._meta.db_table}(before, after)
        SELECT hstore(old), hstore(new);
    RETURN new;
"""

CRUD_TRIGGERS = [
    pgtrigger.Trigger(
        name="track_history_create",
        level=pgtrigger.Row,
        when=pgtrigger.After,
        operation=pgtrigger.Insert,
        func=pgtrigger.Func(TRIGGER_SQL),
    ),
    pgtrigger.Trigger(
        name="track_history_update",
        level=pgtrigger.Row,
        when=pgtrigger.After,
        operation=pgtrigger.Update,
        func=pgtrigger.Func(TRIGGER_SQL),
    ),
    pgtrigger.Trigger(
        name="track_history_delete",
        level=pgtrigger.Row,
        when=pgtrigger.After,
        operation=pgtrigger.Delete,
        func=pgtrigger.Func(TRIGGER_SQL),
    ),
]


class AuditTrigger(models.Model):
    """ """

    class Meta:
        abstract = True
        triggers = CRUD_TRIGGERS
        audit_table = None

    @classmethod
    def check(cls, **kwargs):
        """

        :param kwargs:
        :return:
        """
        errors = super().check(**kwargs)
        errors.extend(cls._check_audit_table(**kwargs))
        errors.extend(cls._check_audit_triggers(**kwargs))
        return errors

    @classmethod
    def _check_audit_table(cls, **kwargs) -> list[checks.Error]:
        """

        :param kwargs:
        :return:
        """
        audit_table = cls.get_audit_table()
        if not audit_table:
            return [
                checks.Error(
                    "no audit table.",
                    hint=f"No audit table defined for {cls}, define an audit_table in the Meta class.",
                    obj=cls,
                    id="django_audimatic.E001",
                )
            ]
        return []

    @classmethod
    def _check_audit_triggers(cls, **kwargs) -> list[checks.Error]:
        """

        :param kwargs:
        :return:
        """
        audit_triggers = cls._get_triggers()
        if not audit_triggers:
            return [
                checks.Error(
                    "no triggers.",
                    hint=f"No triggers defined for {cls}, "
                    "does your Meta class inherit from `AuditTrigger.Meta`?",
                    obj=cls,
                    id="django_audimatic.E002",
                )
            ]
        return []

    @classmethod
    def get_audit_table(cls) -> None | models.Model:
        """

        :return:
        """
        return getattr(cls._meta, "audit_table", None)

    @classmethod
    def _get_triggers(cls) -> list:
        """

        :return:
        """
        return getattr(cls._meta, "triggers", None)

    def get_audit_trail(self) -> models.QuerySet:
        """

        :return:
        """
        audit_table = self.get_audit_table()
        pk = self.id
        return (
            (
                audit_table.objects.filter(before__id__contains=pk)
                | audit_table.objects.filter(after__id__contains=pk)
            )
            .annotate(
                diff=ExpressionWrapper(
                    F("after") - F("before"), output_field=HStoreField()
                )
            )
            .all()
        )


class AuditActions(models.Model):
    """Tracks actions performed on a table.

    When a record is restored from an audit trail, etc.
    """

    action = models.CharField(max_length=128)
    audit_table = models.CharField(max_length=128)
    audit_row_id = models.BigIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        get_user_model(), on_delete=models.DO_NOTHING, null=True, blank=True
    )
